
import datetime
from dateutil.tz import tzutc
import boto
import dateutil.parser
from constance import config
import logging
from virusscan.models import ScanRun
from workermgmt.config import *

# todo image to scanner capabilities mapping


def isolated_connection_factory():
	return boto.connect_ec2_endpoint(config.EC2_URL,
	                                 aws_secret_access_key=config.EC2_SECRET,
	                                 aws_access_key_id=config.EC2_ACCESS)


class DjangolessVMManager(object):
	expiration_delta = datetime.timedelta(days =1)

	def __init__(self):
		self._connection = isolated_connection_factory()
		self.image_type = BASE_IMAGE
		self.logger = logging.getLogger(__name__)

	def _expired_compare(self, instance, test_expired = True ):
		instance_time_launch = dateutil.parser.parse(instance.launch_time)
		expire_deadline = datetime.datetime.now(tz=tzutc()) - self.expiration_delta
		# ensure we don't get a type error from damaging the tz in the above calc
		# < means older than, so instance time launch occurred before expire time
		return instance_time_launch < expire_deadline if test_expired else instance_time_launch >= expire_deadline

	def time_expired(self, instance):
		return self._expired_compare(instance)

	def time_not_expired(self, instance):
		return self._expired_compare(instance, test_expired=False)

	def _get_all_instances_from_reservations(self, reservations):
		l = []
		map(l.extend,[r.instances for r in reservations])
		return l

	def get_workers_reservations_all(self):
		instances = self._connection.get_all_instances(filters={'image-id': self.image_type})
		#filters={"image-id": "ami-7eb54d17","instance-state-name": "running"})
		# todo double check that openstack filters these properly, it will not do so under an admin user
		return instances

	def get_workers_reservations_running(self):
		instances = self._connection.get_all_instances(filters={'image-id': self.image_type,
		                                                        "instance-state-name": "running"})
		return instances

	def get_worker_instances_all(self):

		return self._get_all_instances_from_reservations(self.get_workers_reservations_all())

	def get_worker_instances_running(self):
			return self._get_all_instances_from_reservations(self.get_workers_reservations_running())

	def get_expired_workers(self):
		return filter(self.time_expired, self.get_worker_instances_all())

	def get_non_expired_running_workers(self):
		return filter(self.time_not_expired, self.get_worker_instances_running())

	def create_workers(self, min_count=1, max_count=1, image_type=None):
		if image_type is None:
			image_type = self.image_type
		self._connection.run_instances(image_type, min_count=min_count, max_count=max_count)

	def _term_instances(self, instances):
		if instances:
			self._connection.terminate_instances(instances)
		return instances

	def destroy_all_workers(self):
		return self._term_instances(self.get_worker_instances_all())

	def destroy_all_workers_in_account(self):
		return self._term_instances(self.all_account_instances())

	def all_account_instances(self):
		return self._get_all_instances_from_reservations(self._connection.get_all_instances())

	def _terminate_expired(self):
		expired = self.get_expired_workers()
		self.logger.info("Terminating {0} workers.".format(len(expired)))
		self._term_instances(expired)

	def _terminate_oldest(self):
		self.logger.info("Terminating oldest worker.")
		all_instances = self.get_worker_instances_all()
		self._term_instances(all_instances[0].id)

	def _run_needed(self):
		running = self.get_non_expired_running_workers()
		workers_needed = MINIMUM_WORKERS - len(running)
		if workers_needed > 0:
			self.logger.info("Creating {0} workers.".format(workers_needed))
			self.create_workers(min_count=workers_needed, max_count=workers_needed)

	def maintain(self):
		self._run_needed()
		self._terminate_expired()
		# todo should we spin up new ones first or teardown old ones?

	def autoscale(self):
		pending_scans = self.get_pending_scans()
		workers_running = len(self.get_worker_instances_running())
		autoscale_stats = "Workers: {0} Scans pending: {1}".format(workers_running, pending_scans)
		if (pending_scans / workers_running) > MINIMUM_WORKERS_TO_PENDING_RATIO:
			self.logger.info("Scaling up - currently: {0}".format(autoscale_stats))
			self.create_workers(min_count=1, max_count=1)
			return "Scaling up - currently: {0}".format(autoscale_stats)
		elif ((pending_scans / workers_running) > MAXIMUM_WORKERS_TO_PENDING_RATIO) and (workers_running <= MINIMUM_WORKERS):
			self.logger.info("Scaling down - currently: {0}".format(autoscale_stats))
			self._terminate_oldest()
			return "Scaling down - currently: {0}".format(autoscale_stats)
		self.logger.info("No autoscale action required - currently: {0}".format(autoscale_stats))
		return "No autoscale action required - currently: {0}".format(autoscale_stats)

	def get_pending_scans(self):
		return ScanRun.objects.get_non_expired_pending_scans().count()
