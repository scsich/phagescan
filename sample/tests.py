"""

Run "manage.py test sample".

"""
# -*- coding: utf_8 -*-
from django.core.files import File
from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
import time
from engines.generic.test.common import EICAR_MD5_HEX, EICAR_SHA256_HEX, EICAR_TEST_FILE_PATH, EVIL_PDF_TEST_FILE
from engines.pdfid.scanner import pdfid_engine
from sample.models import FileSample
from virusscan.tests import AbstractScannerHelpers


def make_dj_file_obj_for_tst(path):
	return File(open(path, 'r'))


class AutoFileHashTest(TestCase):
	def test_basic_hashes(self):
		"""
		Test that eicar file is auto-hashed when its made a sample
		"""
		self.user, created = User.objects.get_or_create(username='testuser')
		self.eicar = FileSample.objects.create_sample_from_file_and_user(make_dj_file_obj_for_tst(EICAR_TEST_FILE_PATH), self.user)
		self.assertEqual(EICAR_MD5_HEX, self.eicar.md5)
		self.assertEqual(EICAR_SHA256_HEX, self.eicar.sha256)


class SampleCheckAgainstNSRLTest(TestCase):
	def setUp(self):
		self.user, created = User.objects.get_or_create(username='testuser')
		self.eicar = FileSample.objects.create_sample_from_file_and_user(make_dj_file_obj_for_tst(EICAR_TEST_FILE_PATH), self.user)
		self.evil_pdf = FileSample.objects.create_sample_from_file_and_user(make_dj_file_obj_for_tst(EVIL_PDF_TEST_FILE), self.user)

	def test_check_nsrl_bloom_against_file(self):
		# eicar is in NSRL
		# evil_pdf is not
		unknown_nsrl = FileSample.objects.filter(FileSample.objects.nsrl_unknowns_q())
		self.assertEqual(unknown_nsrl.filter(pk=self.eicar.pk).count(), 0,
						 msg="Found EICAR in query where NSRL entries should be excluded")
		self.assertEqual(unknown_nsrl.filter(pk=self.evil_pdf.pk).count(), 1,
						 msg="Evil PDF did not exist in NSRL excluded query")


class CommonScannerHelpers(TransactionTestCase):
	# WARNING: anything that uses celery to store results needs to use TransactionTestCase or else celery won't see results from other procs

	def _get_scanners_we_care_about(self, we_care, sample):
		res = set(filter(
			lambda x: x.get_scanner_adapter_class() is we_care or isinstance(x.get_scanner_adapter_class(), we_care),
			sample.get_applicable_scanners()))
		return res

	def _test_scanners_that_passed_muster(self, scanners_expected_to_pass_muster, scanners_complete_and_passing_muster):
		self.assertGreater(len(scanners_expected_to_pass_muster), 0,
						   msg="You must expect one or more scanner to pass muster")
		scanners_passing_muster = set()
		# todo filter this list to only virus scanners
		for scanner_result in scanners_complete_and_passing_muster:
			for scanner in scanners_expected_to_pass_muster:
				scanner_class = scanner.get_scanner_adapter_class()
				if scanner_class.name == scanner_result.scanner_type.name:
					scanners_passing_muster.append(scanner)
		self.assertEquals(0, len(scanners_passing_muster.difference(scanners_expected_to_pass_muster)))
		# print "difference: {0}\n".format(len(scanners_passing_muster.difference(scanners_expected_to_pass_muster)))
		# print "pass: {0}\nexpected: {1}\n".format(scanners_passing_muster, scanners_expected_to_pass_muster)


# TODO: This test set has never passed on CI.
#class SampleScanBigCeleryIntegrationTest(AbstractScannerHelpers, CommonScannerHelpers):
#	test_scan_timeout = 10
#
#	def setUp(self):
#		self.user, created = User.objects.get_or_create(username='testuser')
#		self.evil_pdf = FileSample.objects.create_sample_from_file_and_user(make_dj_file_obj_for_tst(EVIL_PDF_TEST_FILE), self.user)
#		self.eicar = FileSample.objects.create_sample_from_file_and_user(make_dj_file_obj_for_tst(EICAR_TEST_FILE_PATH), self.user)
#		# these happen in the background while the other tests run... should start workers first
#		self.worker = self._start_celery_worker_engines()
#		self.master = self._start_celery_master()
#		self.result_saver = self._start_celery_result_saver()
#		self.evil_pdf_result = self.evil_pdf.rescan(timeout=self.test_scan_timeout)
#		self.eicar_result = self.eicar.rescan(timeout=self.test_scan_timeout)
#		# give some time for both to complete and save results ... this needs to be done better though
#		time.sleep(5.0)
#
#	def test_pdf_scans_okay(self):
#		# todo update for other pdf scanners
#		# this will block until all scanning subtasks of master worker are fired off.
#		scanners_that_should_fire_on_pdf = self._get_scanners_we_care_about(pdfid_engine, self.evil_pdf)
#
#		latest_scan = self.evil_pdf.latest_scan()
#		print "scanrun result", latest_scan.scanrunresult_set.values('scanner_type__name')
#		self.assertIsNotNone(latest_scan, msg="No latest scan appeared")
#		pdf_id_result = latest_scan.get_pdfid_scan()
#		self.assertFalse(pdf_id_result.scan_failed(), msg="PDFid scan failed on PDFfile")
#		self._test_scanners_that_passed_muster(scanners_that_should_fire_on_pdf, latest_scan.scanrunresult_set.all())
#
#	def test_eicar_scan_is_infected(self):
#		self.assertTrue(self.eicar.is_infected())
#
#	def test_log_messages_for_all_evilness(self):
#		# todo get all scanners to output evilness
#
#		lastest_scan = self.eicar.latest_scan()
#		self.assertTrue(lastest_scan.is_infected(), "Need an infected result to get log message!")
#		clam_scan = lastest_scan.get_clamav_scan()
#		log_message_str = clam_scan.generate_log_message_str()
#		# todo more intensive checking on required log message constraints
#
#		self.assertIn("Eicar-Test-Signature", log_message_str, "Didn't find right infection string in log message")
#
#	def tearDown(self):
#		self.worker.ensure_shutdown()
#		self.master.ensure_shutdown()
#		self.result_saver.ensure_shutdown()
