
import unittest
import boto
from workermgmt.util import DjangolessVMManager
from constance import config


BASE_IMAGE = u'ami-00000004'


@unittest.skip("Don't have internal EC2 Endpoint yet")
class TestBotoInitial(unittest.TestCase):

	def test_get_workers_with_image(self):
		d = DjangolessVMManager()
		#d.create_workers()
#		workers = d.get_worker_instances_all()
#		d.create_workers()
#		#d.destroy_all_workers()
#		sleep(5)
#		workers_now = d.get_worker_instances_all()
#		d.get_expired_workers()
		d.maintain()
		pass

	def test_boto_connect(self):
		conn = boto.connect_ec2_endpoint(config.EC2_URL, aws_access_key_id=config.EC2_ACCESS, aws_secret_access_key=config.EC2_SECRET)

		nets = conn.get_all_addresses()
		images = conn.get_all_images()
		snaps = conn.get_all_snapshots()
		#conn.run_instances(name)

		#r = conn.run_instances(BASE_IMAGE)
		#ins = conn.get_all_instances(instance_ids=[u'i-00000017'])
		instances = conn.get_all_instances()

		#conn.terminate_instances(instance_ids=[u'i-00000016'])
		pass


