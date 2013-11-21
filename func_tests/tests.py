
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
# from io import StringIO
# import time
# from sample.models import FileSample

# from scanworker.masterworker import MasterWorkerTask

# from workermgmt.views import WorkerAutoscaleTest


class FunctionalTest(TestCase):
	def setUp(self):
		# self.u1 = User.objects.create(username='user1')
		# self.up1 = UserProfile.objects.create(user=self.u1)
		# if not (User.objects.all().filter()):
		c = Client()
		if not (c.login(username='testuser', password='testpass')):
			user = User.objects.create_user('testuser', 'lennon@thebeatles.com', 'testpass')
			c.login(username='testuser', password='testpass')
		# pass


	# def test_upload_process_and_response(self):
	#     c = Client()
	#     CELERY_ALWAYS_EAGER = True
	#     # scanners_to_run = set(VALID_SCANNERS_NO_INSTALL_CHECK())
	#     # result = MasterWorkerTask.delay(8, 8)
	#     # sample = FileSample.objects
	#
	#     print c.login(username='testuser', password='testpass')
	#     # print c.post('/accounts/login/', {'username': 'devuser', 'password': 'devpass'})
	#     with open ("/etc/passwd") as fp:
	#         # response = c.post('/sample/new/add/', {'filename': 'fred', 'file': fp})
	#         response = c.post('/sample/new/add/', {'uploaded_file': fp})
	#         print response
	#     print "Waiting for results from background queue"
	#     # MasterWorkerTask.delay(sample, sample.scanners_to_run)
	#     time.sleep(5)
	#
	#     # print response.content
	#     print response.status_code
	#     response.status_code


	def test_sample_visible(self):
		c = Client()
		c.login(username='testuser', password='testpass')
		response = c.get("/sample/")
		# self.assertEqual(request.contains("Sample"),1)
		# print response.content

		self.assertTrue('Sample' in response.content)

	# def upload_test_gif(self):
	#     # imgfile = None
	#     imgfile = StringIO('GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
	#     # imgfile = 'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
	#     # imgfile.name = 'test_img_file.gif'
	#     # response = self.client.post('/sample/new/add/', {'file': imgfile})
	#     pass