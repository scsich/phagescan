
import datetime
import importlib
import itertools
import operator
import syslog
import boto
from celery import states
from constance import config
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.cache import cache, InvalidCacheBackendError
from django.db.models import Q
from django.db import models
from djorm_hstore.expressions import HstoreExpression as HE
from djorm_hstore.fields import DictionaryField
from djorm_hstore.models import HStoreManager
from djcelery.models import TASK_STATE_CHOICES
from uuid import uuid4
from south.modelsinspector import add_introspection_rules
from engines.generic.abstract import AbstractEvilnessEngine, PLATFORM_CHOICES
from sample.abstract import AbstractFileSample
from scaggr.settings import PENDING_EXPIRE, ARTIFACT_SAVE_DIR, IMAGE_SAVE_DIR, QUEUE_WORKER_CACHE_KEY
from scanworker.file import PickleableFileSample
from scanworker.tasks import VALID_SCANNERS_NO_INSTALL_CHECK, EngineUpdateTask


class TimeoutException(Exception):
	pass


class CantConvertMetadataFileException(Exception):
	pass


class NoScannerWorkerImageInEC2(Exception):
	pass


def get_celery_control():
	import celery
	celery_control = celery.current_app.control
	return celery_control


def isolated_connection_factory():
	return boto.connect_ec2_endpoint(config.EC2_URL, aws_secret_access_key=config.EC2_SECRET,
	                                 aws_access_key_id=config.EC2_ACCESS)


add_introspection_rules([], ["^djorm_hstore\.fields\.DictionaryField"])


def generate_active_q_filter_func(task_q_name):
	def get_active_for_name(entry):
		worker_name, queues_list = entry
		# only include the worker if it has a queue name matching us
		return bool(len(filter(lambda q_dict: q_dict.get('name') == task_q_name, queues_list)))

	return get_active_for_name


def get_active_q_dict_from_cache(inspect=None, reconnect = True):
	# todo fix broken pipe issue when amqp broker gets reset

	def return_active_queue_not_none(aq):
		return aq if aq is not None else dict()

	def get_active_q_dict():
		inspect_ctrl = get_celery_control().inspect() if inspect is None else inspect
		active_q_dict = inspect_ctrl.active_queues()
		return active_q_dict

	try:
		active_q_dict = cache.get(QUEUE_WORKER_CACHE_KEY)
		if active_q_dict is None:
			active_q_dict = get_active_q_dict()
			cache.set(QUEUE_WORKER_CACHE_KEY, active_q_dict, 5.0)

		return return_active_queue_not_none(active_q_dict)
	except InvalidCacheBackendError:
		active_q_dict = get_active_q_dict()
		return return_active_queue_not_none(active_q_dict)
	except:
		raise Exception


class FakeMasterScannerType(object):
	def __init__(self, task_obj):
		self.task_obj = task_obj
		self.active_task = get_active_q_dict_from_cache()

	@property
	def name(self):
		return self.task_obj.name

	def get_all_task_workers(self):
		active_q_dict = get_active_q_dict_from_cache()
		return [wn for wn, ql in filter(generate_active_q_filter_func(self.task_obj.queue), active_q_dict.items())]


class CommonMetadataFileManager(models.Manager):
	use_for_related_fields = True

	def create_metadata_file_from_output(self, incoming_obj):
		# here we need to handle all the possible returned file types that the scan workers could kick out
		# there is only one right now, the picklable file sample
		f = None
		if isinstance(incoming_obj, PickleableFileSample):
			f = ContentFile(incoming_obj.all_content)

		# todo what else would it be? should we raise an exception..?

		if not f:
			raise CantConvertMetadataFileException

		# important or hashing will be all whacked up
		f.seek(0)
		filehash = self.model.filename_hasher(f.read())

		try:
			a = self.get(sha256=filehash)
		except ObjectDoesNotExist:
			a = self.model(sha256=filehash)
			a.filename = incoming_obj.original_filename
			f.seek(0)
			a.file.save(filehash, f)
			a.save()

		return a


class ScanRunResultImageOutput(AbstractFileSample):
	UPLOAD_DIR = IMAGE_SAVE_DIR
	objects = CommonMetadataFileManager()
	filename = models.CharField(max_length=254, default="FILENAME_NOT_SPECIFIED")


class ScanRunResultFileOutput(AbstractFileSample):
	UPLOAD_DIR = ARTIFACT_SAVE_DIR
	objects = CommonMetadataFileManager()
	filename = models.CharField(max_length=254, default="FILENAME_NOT_SPECIFIED")


class ScanRunManager(models.Manager):
	def have_pending_non_expired_scans(self):
		return bool(self.get_non_expired_pending_scans().count())

	def create_pending_scan_run(self, sample, task_id):
		"""
		This creates a pending scan run in the database, it does not actually run the task.
		"""
		return self.create(sample=sample, task_id=task_id)

	def create_pending_scan_run_from_sample(self, task_id):
		"""
		This creates a pending scan run in the database, it does not actually run the task and must be called through the sample
		"""
		return self.create(task_id=task_id)

	def get_latest_scans_distinct_sample(self):
		return self.order_by('sample', 'date_started')

	def get_non_expired_pending_scans(self):
		return self.filter(status__in=[states.PENDING, states.STARTED]).filter(
			date_started__gte=datetime.datetime.utcnow() - PENDING_EXPIRE)

	def have_pending_non_expired_scans(self):
		return bool(self.get_non_expired_pending_scans())

	def get_completed(self):
		return self.filter(status__in=[states.SUCCESS, states.FAILURE])

	def get_latest_completed(self):
		return self.get_completed().latest('date_started')

	def get_latest_pending_completed(self):
		return self.filter(status__in=[states.SUCCESS, states.PENDING, states.STARTED]).latest('date_started')


class ScannerTypeWorkerImageManager(models.Manager):
	@property
	def ec2_connection(self):
		# the attr assignment is here for unit testing so we can shunt in a mocked ec2 connection don't take out!
		if not hasattr(self, '_ec2_connection'):
			self._ec2_connection = isolated_connection_factory()
		return self._ec2_connection

	def get_image_worker_by_image_name_or_create(self, image_label, test_ec2_for_image_exist=False):
		# todo turn on testec2 for image in the default case, for now too many things rely on being able to create without this check
		def inside_create():
			obj = self.model(image_label=image_label)
			obj.save()
			return obj

		try:
			obj = self.get(image_label=image_label)
			return obj
		except self.model.DoesNotExist:
			# we first have to check ec2 to make sure the image exists
			if test_ec2_for_image_exist and self.test_worker_label_exists(image_label):
				return inside_create()
			elif not test_ec2_for_image_exist:
				return inside_create()
		raise NoScannerWorkerImageInEC2()

	def test_worker_label_exists(self, worker_label, instance_list=None):
		return bool(len(self.get_all_instances_running_scanner_image(worker_label, instance_list=instance_list)))

	def get_matching_image_objects(self, image_label, image_list=None):
		# check that just hte image is there ... we don't care about the
		if image_list is None:
			image_list = self.ec2_connection.get_all_images()
		matching_image_list = filter(lambda object: getattr(object, 'name', None) == image_label,image_list)
		return matching_image_list

	def test_worker_image_exists_in_ec2(self, image_label, image_list=None):
		return bool(len(self.get_matching_image_objects(image_label, image_list=image_list)))

	def get_all_instances_running_scanner_image(self, image_name, instance_list=None):
		if instance_list is None:
			instance_list = self.ec2_connection.get_all_instances()

		ami_image_ids_for_image = self.resolve_image_id_to_ami(image_name)

		return filter(lambda x: x.image_id == image_name or x.image_id in ami_image_ids_for_image, itertools.chain.from_iterable(map(operator.attrgetter('instances'), instance_list)))

	def get_all_instances_running_scanner_image_of_states(self, image_name, states, instance_list = None):
		ret =  filter(lambda x: x.state in states, self.get_all_instances_running_scanner_image(image_name, instance_list = instance_list))
		return ret

	def resolve_image_id_to_ami(self, image_label, instance_list = None):
		matching_image_objects =  self.get_matching_image_objects(image_label)
		s = set()
		[s.add(mio.id) for mio in matching_image_objects]
		return s

	def get_all_images(self):
		return self.ec2_connection.get_all_images()

	def spin_up_workers(self):

		# the dict goes image-label : needed count
		current_image_list = self.get_all_images()
		# todo check default instance type
		# todo make sure that the couldn't start images are processed or raise an exception
		# todo there is no way to link hostname on celery queue and instance yet
		couldnt_start_images = []
		# todo burn down instances if ness
		for active_worker_image in self.get_active_worker_images():
			try:
			# todo figure out how to do instance type properly
				active_worker_image.spin_up(image_list=current_image_list)
			except NoScannerWorkerImageInEC2:
				couldnt_start_images.append(active_worker_image.image_label)
		return couldnt_start_images

	def terminate_all(self):
		return map(ScannerTypeWorkerImage.terminate, self.all())

	def get_active_worker_images(self):
		# get the list of images that actually have scanner types attached
		return self.filter(scannertype__isnull=False).distinct('pk')

	def get_worker_image_set(self):
		return self.get_active_worker_images().values_list('image_label', flat=True)


class ScannerTypeWorkerImage(models.Model):
	image_label = models.CharField(max_length=128, null=False, unique=True)
	# todo make sure these choices are accurate
	instance_type = models.CharField(max_length=32,
	                                 choices=[('m1.small', "small"), ('m1.medium', "medium"), ('m1.large', "large")],
	                                 default="m1.medium", null=False, blank=False)
	needed_copies = models.PositiveSmallIntegerField(default = 1, null = False, blank = False)
	objects = ScannerTypeWorkerImageManager()

	def __unicode__(self):
		return self.image_label

	@property
	def ec2_connection(self):
		return ScannerTypeWorkerImage.objects.ec2_connection

	def worker_image_exists_in_ec2(self, image_list = None):
		return ScannerTypeWorkerImage.objects.test_worker_image_exists_in_ec2(self.image_label, image_list=image_list)

	def spin_up(self, image_list = None):
		if self.worker_image_exists_in_ec2(image_list=image_list):
			needed = self.calculate_needed_image_copies()
			return self.ec2_connection.run_instances(self.image_label, min_count=needed, max_count=needed,
				                                  instance_type=self.instance_type, key_name=config.EC2_KEYPAIR, user_data=config.EC2_USERDATA)
		raise NoScannerWorkerImageInEC2

	def terminate(self):
		self.ec2_connection.terminate_instances(instance_ids=map(operator.attrgetter('id'), self.get_all_pending_running_instances()))

	def get_running_instances(self):
		# todo make sure this status code is right
		return ScannerTypeWorkerImage.objects.get_all_instances_running_scanner_image_of_states(self.image_label, ['running'])

	def get_pending_instances(self):
		return ScannerTypeWorkerImage.objects.get_all_instances_running_scanner_image_of_states(self.image_label, ['pending'])

	def get_all_pending_running_instances(self):
		r =  self.get_pending_instances() + self.get_running_instances()
		return r

	def calculate_needed_image_copies(self):
		# todo right now this is a simple static value and we'll teardown/spin up new images every time without seeing whats there
		return self.needed_copies


class ScannerTypeManager(models.Manager):
	def set_active_by_q_dict(self, q_dict):
		all_active_names = set()
		for wq in q_dict.values():
			map(all_active_names.add, [qdef['name'] for qdef in wq])

		if len(all_active_names) != 0:
			q_object = reduce(operator.ior,  [Q(name__iexact = name) for name in all_active_names])
			scanners_to_update = ScannerType.objects.filter(q_object)
			scanners_to_update.update(active_workers = True)

			scanners_to_deactivate = ScannerType.objects.filter(~Q(pk__in = scanners_to_update))
			scanners_to_deactivate.update(active_workers = False)
		else:
			scanners_to_deactivate = ScannerType.objects.all()
			scanners_to_deactivate.update(active_workers = False)

	def get_active_scanners_for_display(self):
		return self.filter(scanrunresult__isnull = False).distinct('pk')

	def get_scanner_by_adapter(self, scan_adapter_class_def_or_class_uninst):
		scan_adapter_class_def_or_class = scan_adapter_class_def_or_class_uninst
		if isinstance(scan_adapter_class_def_or_class.name, property):
			# instantiate the class so we don't get raw property strings!
			scan_adapter_class_def_or_class = scan_adapter_class_def_or_class()
		mod_str = ".".join(
			[scan_adapter_class_def_or_class.__class__.__module__, scan_adapter_class_def_or_class.__class__.__name__])

		try:
			return self.get(name=scan_adapter_class_def_or_class.name,
			                platform=scan_adapter_class_def_or_class.platform,
			                class_name=mod_str)
		except self.model.DoesNotExist:
			obj = self.model(name=scan_adapter_class_def_or_class.name,
			                 platform=scan_adapter_class_def_or_class.platform,
			                 class_name=mod_str)
			# associate the default worker image on creation
			obj.worker_image = ScannerTypeWorkerImage.objects.get_image_worker_by_image_name_or_create(
				self.get_default_worker_image_label_for_name(scan_adapter_class_def_or_class.name))
			obj.save()
			if isinstance(scan_adapter_class_def_or_class, AbstractEvilnessEngine):
				obj.is_evilness = True
				obj.save()
			return obj
		except:
			raise self.model.DoesNotExist()

	def get_scanner_by_task(self, scan_task):
		adapter = scan_task()._import_scanner()()
		return self.get_scanner_by_adapter(adapter)

	def create_all_valid_scanner_db_entries(self):
		return map(self.get_scanner_by_task, VALID_SCANNERS_NO_INSTALL_CHECK())

	def get_default_worker_image_label_for_name(self, name):
		try:
			image_label = config.__getattr__("{0}_EC2_IMAGE".format(name))
			return image_label
		except AttributeError:
			return config.DEFAULT_WORKER_IMAGE_MAPPING
		except:
			raise AttributeError()


class ScannerType(models.Model):
	objects = ScannerTypeManager()
	is_evilness = models.BooleanField(default=False)
	name = models.CharField(max_length=128, null=False)
	class_name = models.CharField(max_length=254, null=False)
	platform = models.CharField(max_length=128, choices=PLATFORM_CHOICES, null=False)
	worker_image = models.ForeignKey(ScannerTypeWorkerImage, null=False)
	active_workers = models.BooleanField(default = True)

	def get_short_name(self):
		return self.name.split('.')[-1]

	def get_worker_image_label(self):
		return self.worker_image.image_label

	def get_sample_detail_display_template(self):
		"""
		This gets the sample display html template for inclusion
		"""
		sample_display = getattr(self,
		                         '_sample_detail_display_template',
		                         dict()).get(self.name,
		                                     'sampledisplay/{0}.html'.format(self.get_short_name()))
		return sample_display

	def get_scanner_task_class(self):
		task_mod = importlib.import_module("scanworker.tasks")
		task_class = eval('task_mod.{0}'.format(self.name.lower()))
		task_class.declare_celery_queue()
		return task_class

	@property
	def mod_and_class_str(self):
		parts = self.class_name.split(".")
		assert (len(parts) > 1)
		class_name = parts.pop()
		mod_str = ".".join(parts)

		return mod_str, class_name

	def get_scanner_engine_class(self):
		mod_str, class_name = self.mod_and_class_str
		imported_mod = importlib.import_module(mod_str)

		return eval(".".join(["imported_mod", class_name]))

	@property
	def task_q_name(self):
		if not hasattr(self, '_task_q_name'):
			# have to instantiate class here or else we get property object
			self._task_q_name = self.get_scanner_engine_class()().q_name
		return self._task_q_name

	def get_update_task(self, targeted_worker):

		return EngineUpdateTask

	def get_all_task_workers(self):
		active_q_dict = get_active_q_dict_from_cache(
			inspect=None if not hasattr(self, '_celery_test_inspect') else self._celery_test_inspect)
		return [wn for wn, ql in filter(generate_active_q_filter_func(self.task_q_name), active_q_dict.items())]

	def create_update_queue_for_targeted_worker(self, targeted_worker):
		get_celery_control().add_consumer(targeted_worker, destination=[targeted_worker])

	def offline_targeted_worker(self, targeted_worker):
		get_celery_control().cancel_consumer(self.task_q_name, destination=[targeted_worker])

	def online_targeted_worker(self, targeted_worker):
		get_celery_control().add_consumer(self.task_q_name, routing_key=self.task_q_name, destination=[targeted_worker])

	# todo put master side of definitions here
	def update_targeted_worker(self, targeted_worker, update_file=None):
		# algorithm is to offline a worker on a queue one at a time then update it and confirm
		# target each worker with a specific routing message
		self.create_update_queue_for_targeted_worker(targeted_worker)
		scanner = self.get_scanner_engine_class()()
		if scanner.requires_update_file_from_master:
			defn_update_file_factory_func = scanner.get_update_file_factory()
			defn_file = defn_update_file_factory_func() if update_file is None else update_file
			# get the update task for this scanner and fire the file at it
			update_by_file_task = self.get_update_task(targeted_worker)

			return update_by_file_task.subtask((self.get_scanner_engine_class(), defn_file ), queue=targeted_worker)
		else:
			return self.get_update_task(targeted_worker).subtask((self.get_scanner_engine_class(), ),
			                                                     queue=targeted_worker)

	# TODO: I don't think this is used. All of the engine tests call the update_definitions() in their engine class.
	# def update_definitions(self):
	# 	all_workers_for_scanner = self.get_all_task_workers()
	# 	map(self.update_targeted_worker, all_workers_for_scanner)

	def __str__(self):
		return "%s/%s" % (self.name, self.platform)

	class Meta:
		unique_together = (('name', 'platform'),)


class ScanRun(models.Model):
	objects = ScanRunManager()

	sample = models.ForeignKey('sample.FileSample')
	date_started = models.DateTimeField(auto_now_add=True)

	# to provide minimal task tracking while still being able to use amqp result backend
	task_id = models.CharField("task id", max_length=255, unique=True)
	status = models.CharField("state", max_length=50, default=states.PENDING, choices=TASK_STATE_CHOICES)
	# todo put a date done in there?

	def __str__(self):
		return "{0} {1}".format(self.sample, self.date_started)

	def is_infected(self):
		infected = self.scanrunresult_set.get_infected()
		iif = infected.count()
		return bool(iif)

	def get_number_infections(self):
		try:
			infected = self.scanrunresult_set.get_infected()
			l = list(infected)
			return infected.count()
		except IndexError:
			return None

	def get_number_evilness_scanners(self):
		# todo exclude ones with tracebacks
		return self.scanrunresult_set.get_evilness().count()

	def get_number_evilness_failures(self):
		return self.scanrunresult_set.get_evilness_failures().count()

	def get_number_clean(self):
		try:
			not_infected = self.scanrunresult_set.get_not_infected()
			return not_infected.count()
		except IndexError:
			return None

	def get_most_informational_scan_result(self):
		# min infection string wins that is over 4 chars
		try:
			infecteds = self.scanrunresult_set.get_infected()
			# todo return first scan run if we're not infected
			if infecteds.count():
				infecteds = filter(lambda z: len(z.metadata.get('infected_string', '')) > 4, infecteds)
				return min(infecteds, key=lambda x: len(x.metadata.get('infected_string', '')))
			else:
				# no tracebacks first ...
				return self.scanrunresult_set.order_by('-traceback')[0]
		except ValueError:
			return None

	# todo: generate these functions dynamically?
	def get_oms_scan(self):
		from engines.officemalscanner.scanner import officemalscanner_engine as oms

		return self.scanrunresult_set.get(scanner_type__name=oms().name)

	def get_pdfid_scan(self):
		from engines.pdfid.scanner import pdfid_engine as pdfid

		return self.scanrunresult_set.get(scanner_type__name=pdfid().name)

	def get_opaf_scan(self):
		from engines.opaf.scanner import opaf_engine as opaf

		return self.scanrunresult_set.get(scanner_type__name=opaf().name)

	def get_peid_scan(self):
		from engines.peid.scanner import peid_engine as peid

		return self.scanrunresult_set.get(scanner_type__name=peid().name)

	def get_clamav_scan(self):
		from engines.clamav.scanner import clamav_engine as clamav

		return self.scanrunresult_set.get(scanner_type__name=clamav().name)

	def _extract_file_fields_if_exist(self, scan_result, scan_run_result_db):
		try:
			images = scan_result.images
			files = scan_result.files
			# then we've got to add each of these because they're not necessarily linked yet
			scan_run_result_db.image_output.add(
				*map(ScanRunResultImageOutput.objects.create_metadata_file_from_output, images))
			scan_run_result_db.file_output.add(
				*map(ScanRunResultFileOutput.objects.create_metadata_file_from_output, files))
		except AttributeError:
			# then we're a evilness result and we don't have these fields
			pass

	def _update_metadata_if_evilness(self, actual_result):
		try:
			if actual_result.infected_string is not None:
				actual_result.metadata['infected_string'] = actual_result.infected_string
				actual_result.metadata['infected'] = actual_result.infected
		except AttributeError:
			# then our result doesn't have them ... dont worry about it
			pass

	def populate_scan_run_result_from_scanner(self, scan_result, timeout=2.0, populate_for_timeouts=False):
		actual_result = scan_result.get(timeout=timeout)
		scan_run_result_db = self.scanrunresult_set.get(task_id=scan_result.id)
		self._update_metadata_if_evilness(actual_result)
		# todo serialize nested metadata better
		# todo make this an update instead of a get/save
		scan_run_result_db.metadata = actual_result.metadata
		scan_run_result_db.pending = False
		scan_run_result_db.traceback = ''
		scan_run_result_db.save()

		self._extract_file_fields_if_exist(actual_result, scan_run_result_db)
		scan_run_result_db.syslog_if_first_infected()

	def create_db_entry_for_scan_task(self, celery_scan_task_or_result, django_task_type_model_entry, traceback = None, pending = True):
		task_id = None
		if celery_scan_task_or_result is None:
			# fake it if we don't have to do a task
			task_id = str(uuid4())
		else:
			task_id = celery_scan_task_or_result.id
		return self.scanrunresult_set.create(task_id=task_id,
		                                     scanner_type=django_task_type_model_entry, pending = pending, traceback=traceback)

	def get_scan_tasks_and_create_pending_db_entries(self, timeout=20):
		scanner_types = ScannerType.objects.all()
		initd_subtasks = []

		for task_type_db in scanner_types:

			# Queues object below is required as a collection of queues that are eventually consumed by amqp

			db_entry = None
			scanner_task = task_type_db.get_scanner_task_class()
			# timeout is now handled by queue message expiration at the rabbit level
			sub_task = scanner_task.subtask((self.sample.get_pickleable_file(),))
			# force an id
			sub_task._freeze()

			if task_type_db.active_workers:
				db_entry = self.create_db_entry_for_scan_task(sub_task, task_type_db)

			else:
				db_entry = self.create_db_entry_for_scan_task(sub_task,
				                                              task_type_db,
				                                              traceback="No active worker for task at launch time",
				                                              pending=False)
				sub_task = None
			initd_subtasks.append((sub_task, db_entry))
		return initd_subtasks

	def _mark_state_and_save(self, state):
		if self.status != state:
			self.status = state
			self.save()

	def mark_started(self):
		self._mark_state_and_save(states.STARTED)

	def mark_finished(self):
		self._mark_state_and_save(states.SUCCESS)

	def check_tasks_and_mark_finished(self):
		pending_failures = self.scanrunresult_set.get_pending()
		pending_failures.update(traceback="Scan request not taken off queue within timeframe. Marked as failed, but could come in later.")
		self.mark_finished()


class ScanRunResultManager(HStoreManager):
	def get_failed(self):
		return self.exclude(traceback=None)

	def get_infected(self):
		return self.get_evilness().filter(Q(metadata__contains='infected_string')).where(
			~HE("metadata").contains({'infected_string': ''}))

	def get_not_infected(self):
		return self.get_evilness().filter(metadata__contains='infected_string').where(
			HE("metadata").contains({'infected_string': ''}))

	def get_evilness(self):
		return self.filter(scanner_type__is_evilness=True)

	def get_evilness_failures(self):
		return self.get_evilness().filter(~Q(metadata__contains='infected_string') & ~Q(traceback=''))

	def get_pending(self):
		return self.filter(pending=True)


class ScanRunResult(models.Model):
	"""
	Storage for results of scan runs.

	Fields:
	scanner_type		ForeignKey -> ScannerType
	scan_run			ForeignKey -> ScanRun

	traceback			TextField

	Things to think about:
	* how do we want to store errors out of scan backends
	"""

	# Domestic Keys on top of base class
	scanner_type = models.ForeignKey(ScannerType, null=False)
	scan_run = models.ForeignKey(ScanRun)
	file_output = models.ManyToManyField(ScanRunResultFileOutput)
	image_output = models.ManyToManyField(ScanRunResultImageOutput)
	pending = models.BooleanField(default=True)
	# traceback is for errors (when infected == NULL)
	traceback = models.TextField("traceback", blank=True, null=True)
	metadata = DictionaryField()
	task_id = models.CharField(max_length=128, null=False)

	def scan_succeeded(self):
		return self.traceback is None or self.traceback == ''

	def scan_failed(self):
		return not (self.scan_succeeded())

	def get_peid_metadata(self):
		d = self.metadata.copy()
		for k, v in d.items():
			try:
				d[k] = eval(v)
			except SyntaxError, NameError:
				pass
			except:
				pass

		def colorize(import_name):
			color = 'black'
			if import_name in ['LoadLibraryA']:
				color = 'red'
			return import_name, color

		for dllname, imports in d['imported_dlls'].items():
			imports = map(colorize, imports)
			d['imported_dlls'][dllname] = imports

		return d

	@property
	def infected_string(self):
		return self.metadata.get('infected_string', None)

	@property
	def infected(self):
		return self.infected_string != '' and self.infected_string is not None

	def has_previous_infected_result(self):
		return self.__class__.objects.get_infected().filter(scan_run__sample=self.scan_run.sample).filter(
			scanner_type=self.scanner_type).exclude(pk=self.pk)

	@property
	def engine_version(self):
		return self.metadata[AbstractEvilnessEngine.ENGINE_VERSION_KEY]

	@property
	def definition_version(self):
		return self.metadata[AbstractEvilnessEngine.DEFINITION_VERSION_KEY]

	def generate_log_message_str(self):
		cef_delim = "|"
		device_vendor = "Narf Ind"
		device_product = "PhageScan"
		device_version = "0.5b"
		name = 'infected file detected'

		cef_prefix = "CEF:0"
		scanner_type = self.scanner_type.get_short_name()

		scanner_version = self.engine_version
		scanner_defn_version = self.definition_version

		signature_id = scanner_type
		severity = 8

		sample_sha = self.scan_run.sample.file_hash()
		cef_fields = [
			cef_prefix,
			device_vendor,
			device_product,
			device_version,
			signature_id,
			name,
			severity,
		]

		extension = {
		'sha256': sample_sha,
		'engine_version': scanner_version,
		'definition_version': scanner_defn_version,
		'infected_string': self.infected_string,
		}

		# k=v<space>k=v<space>
		cef_fields = map(str, cef_fields)
		extension_string = " ".join(["{0}={1}".format(k, v) for k, v in extension.items()])
		return cef_delim.join((cef_fields + [extension_string]))

	def syslog_if_first_infected(self):
		if self.scanner_type.is_evilness and not self.has_previous_infected_result():
			# then we can syslog this for the first time
			msg_str = self.generate_log_message_str()
			syslog.syslog(msg_str)

	objects = ScanRunResultManager()

	class Meta:
		unique_together = (('scanner_type', 'scan_run'))
