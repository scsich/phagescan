
from django.contrib.auth.models import User
from django.test import TestCase
from accounts.models import Account
from virusscan.models import ScanRun
from engines.generic.test.common import CLEAN_TEST_FILE_PATH
from sample.models import FileSample
from virusscan.tests import move_to_media_dir
from uuid import uuid4
from os import remove
from os.path import basename


class CommonModelSetup(TestCase):

	def setUp(self):
		self.f = move_to_media_dir(CLEAN_TEST_FILE_PATH)
		self.user, created = User.objects.get_or_create(username='hithere')
		self.inert, created = FileSample.objects.get_or_create(file=self.f, user=self.user)
		self.inert.attach_new_filename(basename(self.f))

	def tearDown(self):
		remove(self.f)
		super(TestCase, self).tearDown()


class AccountsModelsTest(CommonModelSetup):

	def test_api_key(self):
		acc = Account()
		acc.user = self.user
		key = acc.get_api_key()
		self.assertIsNotNone(key, msg="API key is none.")

	def test_get_pending_scans_empty(self):
		acc = Account()
		acc.user = self.user
		pending = acc.get_pending_scans()
		self.assertQuerysetEqual(pending, [])

	def test_get_pending_scans_not_empty(self):
		acc = Account()
		acc.user = self.user

		fake_task_id = str(uuid4())
		run = ScanRun.objects.create_pending_scan_run(self.inert, fake_task_id)
		pending = acc.get_pending_scans()
		#  pending == ['<ScanRun: 3 2013-08-19 14:37:56.165701+00:00>']
		self.assertTrue(isinstance(pending[0], ScanRun),
		                msg='Pending scan object is not of instance of ScanRun: {0}'.format(pending[0]))

	def test_get_samples(self):
		acc = Account()
		acc.user = self.user
		fake_task_id = str(uuid4())
		run = ScanRun.objects.create_pending_scan_run(self.inert, fake_task_id)
		sample = acc.get_samples()
		# sample = [<FileSample: 4>]
		self.assertTrue(isinstance(sample[0], FileSample),
		                msg='Sample object is not instance of FileSample: {0}'.format(sample[0]))

# TODO: Make test(s) of accounts views
#
# class CommonViewSetup(TestCase):
#
# 	def setUp(self):
# 		self.user, created = User.objects.get_or_create(username = 'hithere', password='easy')
# 		self.factory = RequestFactory()
#
#
# 	# def tearDown(self):
# 	# 	remove(self.f)
#
# class AccountDetailViewTest(CommonViewSetup):
#
#
# 	def test_view_response(self):
# 		# acc = Account()
# 		# acc.user = self.user
# 		# key = acc.get_api_key()
# 		# self.assertIsNotNone(key, msg="API key is none.")
# 		request = self.factory.get('/accounts/')
# 		request.user = self.user
# 		response = AccountDetailView()
# 		self.assertEqual(response.status_code, 200)
