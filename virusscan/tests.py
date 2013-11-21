"""

Run "manage.py test".

"""
# -*- coding: utf_8 -*-
from operator import attrgetter
import tempfile
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings
from celery import states
from uuid import uuid4
from shutil import copyfile
from os import mkdir, remove, path
import boto
from moto import mock_ec2
from constance import config
from engines.yara.test.testscan import CommonYaraHelpers, EICAR_TESTING_UPDATE_STRING
from engines.generic.test.common import CLEAN_TEST_FILE_PATH, EICAR_TEST_FILE_PATH, _make_eicar_picklable_file_object
from sample.models import FileSample
from virusscan.models import ScanRun, ScannerType, ScannerTypeWorkerImage
from virusscan.t_util import Worker, ResultSaver, Master
from engines.yara.scanner import yara_engine
from engines.yara.scanner import OTHER_INFECTED_DICT_K
from engines.clamav.scanner import clamav_engine


EICAR_TEST_FILE = 'eicar.com.txt'
INERT_TEST_FILE = 'blat.ex_'
PROJECT_ROOT = path.abspath(path.join(path.dirname(__file__), path.pardir))


# Test are run with DEBUG=False, so it seems that we can only access files in the /media/ directory.
# That means we have to create that dir and we have to copy testing sample files there:
def move_to_media_dir(file_path):
	media_dir = path.join(PROJECT_ROOT, 'media')
	if not path.exists(media_dir): mkdir(media_dir)
	file_in_media = path.join(media_dir, path.basename(file_path))
	copyfile(file_path, file_in_media)
	return file_in_media


@override_settings(CELERY_ALWAYS_EAGER=True, BROKER_BACKEND='memory',)
class CommonSetup(TestCase):

	def setUp(self):
		self.cav_engine = clamav_engine
		t = self.cav_engine()
		self.assertEqual(t.is_installed(), True, msg="ClamAV needs to be installed to test basic scan runs!")
		self.EICAR_MEDIA_PATH = move_to_media_dir(EICAR_TEST_FILE_PATH)
		self.INERT_MEDIA_PATH = move_to_media_dir(CLEAN_TEST_FILE_PATH)
		self.user, created = User.objects.get_or_create(username='hithere')
		self.eicar, created = FileSample.objects.get_or_create(file=self.EICAR_MEDIA_PATH, user=self.user)
		self.inert, created = FileSample.objects.get_or_create(file=self.INERT_MEDIA_PATH, user=self.user)
		self.eicar.attach_new_filename(path.basename(self.EICAR_MEDIA_PATH))
		self.inert.attach_new_filename(path.basename(self.INERT_MEDIA_PATH))

	def tearDown(self):
		remove(self.EICAR_MEDIA_PATH)
		remove(self.INERT_MEDIA_PATH)


class ScannerModelsTest(CommonSetup):

	def _check_run_for_n_result(self, run, expected_result, n=1):
		self.assertEqual(run.scanrunresult_set.count(), n)
		for scan_result in run.scanrunresult_set.all():
			# ensure that all show up equal
			self.assertTrue(scan_result.scan_succeeded(),
			                msg="Scan result had a non null traceback msg, some failure occurred {0}.".format(scan_result.traceback))
			self.assertEqual(scan_result.infected ,expected_result,
			                 msg="Did not get an %s result where we thought we should {0}.".format(expected_result, scan_result.scanner_type.name))

	def _do_basic_scanrun(self, expected_infected_result, sample_obj):
		fake_task_id = str(uuid4())
		run = ScanRun.objects.create_pending_scan_run(sample_obj, fake_task_id)
		self.assertEqual(states.PENDING, run.status)

		task_type_db = ScannerType.objects.get_scanner_by_adapter(self.cav_engine)
		celery_task_for_task_type = task_type_db.get_scanner_task_class()
		task_result = celery_task_for_task_type.delay(sample_obj.get_pickleable_file())

		# this one is necessary to populate the DB entry before this goes out see: ScanRun.populate_scan_run_result_from_scanner
		run.create_db_entry_for_scan_task(task_result, task_type_db)
		run.populate_scan_run_result_from_scanner(task_result)

		self._check_run_for_n_result(run, expected_infected_result)

	def test_basic_scanrun_hit(self):
		self._do_basic_scanrun(True, self.eicar)

	def test_basic_scanrun_nohit(self):
		self._do_basic_scanrun(False, self.inert)


class AbstractScannerHelpers(object):
	@property
	def test_host_name(self):
		# randomize this per class instantiation to minimize the chance that old failed iterations will help us fail
		import uuid
		random_val = str(uuid.uuid1())[:8]
		return 'celery_testing_host.{0}'.format(random_val)

	def _filter_worker_list_for_test_host(self, l):
		return filter(lambda x: x == self.test_host_name, l)

	def _start_celery_worker_engines(self):
		w = Worker(self.test_host_name)
		w.ensure_started()
		return w

	def _start_celery_master(self):
		m = Master(self.test_host_name)
		m.ensure_started()
		return m

	def _start_celery_result_saver(self):
		r = ResultSaver(self.test_host_name)
		r.ensure_started()
		return r

	def _get_yara_engine_db_scanner(self):
		db_scanner_type = ScannerType.objects.get_scanner_by_adapter(yara_engine())
		return db_scanner_type


class ScannerOnlineOfflineQueueTest(TestCase, AbstractScannerHelpers):

	# TODO: This test is failing on CI
	def test_basic_on_queue_down_queue(self):
		try:
			w = self._start_celery_worker_engines()

			db_scanner_type = self._get_yara_engine_db_scanner()
			assert(str(db_scanner_type.name).lower() == 'yara')
			all_workers = self._filter_worker_list_for_test_host(db_scanner_type.get_all_task_workers())
			self.assertEqual(len(all_workers), 1, msg="Failed to start worker with test yara Q.")
			db_scanner_type.offline_targeted_worker(self.test_host_name)
			all_workers = self._filter_worker_list_for_test_host(db_scanner_type.get_all_task_workers())
			self.assertEqual(len(all_workers), 0, msg="Failed to offline worker with test yara Q.")
			# then we check if we're there again
			db_scanner_type.online_targeted_worker(self.test_host_name)
			all_workers = self._filter_worker_list_for_test_host(db_scanner_type.get_all_task_workers())
			self.assertEqual(len(all_workers), 1, msg="Failed to re-online worker with test yara Q.")
		finally:
			w.ensure_shutdown()

	# def test_yara_update_through(self):
	# 	try:
	# 		w = self._start_celery_worker_engines()
	# 		# todo take a yara test config with no relevant signatures and run a file through it
	# 		# todo then take a
	# 	finally:
	# 		w.ensure_shutdown()


class TestYaraUpdates(CommonYaraHelpers, AbstractScannerHelpers, TestCase):
	def setUp(self):
		from constance import config
		self.test_repo_update_url = config.YARA_REPO_URL
		self.evil_file_object = _make_eicar_picklable_file_object()
		self.temp_repo_dir = tempfile.mktemp()

		self._scanner = yara_engine(repo_rules_dir=self.temp_repo_dir)
		self.scanner = self._scanner

		self.w = self._start_celery_worker_engines()

		self._clone_and_create_update_tar()

	def _clone_and_create_update_tar(self):
		import vcs
		g = vcs.get_backend('git')
		self.gr = g(self.temp_repo_dir, src_url=self.test_repo_update_url, create=True, update_after_clone=True)

		self.update_file_factory_func = self._scanner.get_update_file_factory()

	def _check_for_rule_hits_matching_new_eicar(self, all_rule_hits):
		new_rule_hits = filter(
			lambda other_infect_entry: other_infect_entry.get('rule', False) == EICAR_TESTING_UPDATE_STRING,
			all_rule_hits)
		return new_rule_hits

	def test_yara_update_task_works(self):
		self._scanner._clear_rule_dir()
		yara_django_obj = self._get_yara_engine_db_scanner()
		scanner_task = yara_django_obj.get_scanner_task_class()

		result = scanner_task.apply_async(args=(self.evil_file_object,))
		generic_evilness_result = result.get(timeout=5)

		self.assertEqual(generic_evilness_result.metadata['definitions'],
		                 'Unknown',
		                 msg="No version number should be present before update.")
		new_rule_hits = self._check_for_rule_hits_matching_new_eicar(generic_evilness_result.metadata.get(OTHER_INFECTED_DICT_K, list()))

		self.assertEqual(len(new_rule_hits), 0, msg="New eicar rule shouldn't be there before the update.")
		# now we update and we should have the new rule hit after we fire the other task
		update_tar = self.update_file_factory_func()
		sut = yara_django_obj.update_targeted_worker(self.test_host_name, update_file=update_tar)
		r = sut.delay()
		rr = r.get(timeout=5)

		scanner_task = yara_django_obj.get_scanner_task_class()

		result = scanner_task.delay(self.evil_file_object)
		generic_evilness_result = result.get(timeout=5)

		new_rule_hits = self._check_for_rule_hits_matching_new_eicar(generic_evilness_result.metadata.get(OTHER_INFECTED_DICT_K, list()))
		self.assertNotEqual(generic_evilness_result.metadata['definitions'],
		                    'Unknown',
		                    msg="A version number must be present after update.")
		self.assertEqual(len(new_rule_hits),
		                 1,
		                 msg="New eicar rule should be there after the update {0}.".format(generic_evilness_result.metadata))

	def tearDown(self):
		self.w.ensure_shutdown()
		super(TestYaraUpdates, self).tearDown()


class ScannerWorkerGeneric(object):
	def setUp(self):
		self.ec2_mock = mock_ec2()
		self.ec2_mock.start()

		self.ec2_connect = boto.connect_ec2(config.EC2_SECRET, config.EC2_ACCESS)
		self._copy_mocked_ec2_conn()
		ScannerType.objects.create_all_valid_scanner_db_entries()
		self.instance_image_tags = ScannerTypeWorkerImage.objects.get_worker_image_set()
		# have to make sure we have valid scanner types

		# have to add each image type to the mocked back end before we try the individual scanner type
		for image_tag in self.instance_image_tags:
			reservation = self.ec2_connect.run_instances(image_tag)
			instances = reservation.instances
			i = self.ec2_connect.create_image(instances[0].id, image_tag, description="test image")
			# got this syntax from the mock tests
			self.ec2_connect.terminate_instances(map(attrgetter('id'), instances))
		# even though the instances are terminated Ec2 will still have them there in shutting down state
		self.assertNotEqual(0, ScannerType.objects.count())

	def _copy_mocked_ec2_conn(self):
		ScannerTypeWorkerImage.objects._ec2_connection = self.ec2_connect

	def tearDown(self):
		self.ec2_mock.stop()


class ScannerWorkerTest(ScannerWorkerGeneric, TestCase):

	def setUp(self):
		ScannerType.objects.create_all_valid_scanner_db_entries()
		x = ScannerType.objects.all()[0]
		# this needs to be done to avoid the rabbit error
		x.get_all_task_workers()
		ScannerWorkerGeneric.setUp(self)

	def test_correct_worker_spawn_all_em_terminate_too(self):

		couldnt_start = ScannerTypeWorkerImage.objects.spin_up_workers()
		self.assertEqual(0, len(couldnt_start))
		for scanner_type in ScannerType.objects.all():
			# we shouldn't need anymore workers after we've spun everyone up
			self.assertEqual(len(scanner_type.worker_image.get_all_pending_running_instances()), 3)

		ScannerTypeWorkerImage.objects.terminate_all()

		for scanner_type in ScannerType.objects.all():
			# we do this for scanner type to make sure they all yield the same results
			final_instances = scanner_type.worker_image.get_all_pending_running_instances()
			self.assertEqual(len(final_instances), 0, msg="Should have terminating instances!")


class IndividualScannerCreationTest(ScannerWorkerGeneric, TestCase):
	def test_individual_scanner_creation(self):
		for scanner_type in ScannerType.objects.all():
			self.assertTrue(scanner_type.worker_image.worker_image_exists_in_ec2(),
			                msg="Couldn't find image for {0}.".format(scanner_type.get_worker_image_label()))