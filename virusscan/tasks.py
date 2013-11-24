
from datetime import timedelta
from celery.task import PeriodicTask, Task
from celery.utils.log import get_task_logger


class RescanNonExpiredNonInfectedFiles(PeriodicTask):
	"""
	Periodic re-scan task that ensures updated virus definitions are used against files we thought clean in the past.
	"""
	queue = 'RescanNonExpiredNonInfectedFiles'
	routing_key = 'RescanNonExpiredNonInfectedFiles'
	run_every = timedelta(hours=6)
	logger = get_task_logger(__name__)

	def run(self):
		self.logger.debug("Starting rescan of non-expired, non-infected files.")
		from sample.models import FileSample
		map(FileSample.rescan, FileSample.objects.samples_for_periodic_rescan())


#class EngineActiveMarkerTask(PeriodicTask):
class EngineActiveMarkerTask(Task):
	"""
	Periodic task to ensure active_queue status is updated.

	This is only used in production.
	To enable,
	- change class inheritance from 'Task' to 'PeriodicTask' above
	- uncomment 'run_every' class variable below.
	"""
	ignore_result = True
	queue = 'EngineActiveMarkerTask'
	routing_key = 'EngineActiveMarkerTask'
	#run_every = timedelta(minutes=15)
	logger = get_task_logger(__name__)

	def run(self):
		self.logger.debug("Starting EngineActiveMarkerTask.")
		# to protect against other imports
		from virusscan.models import ScannerType, get_active_q_dict_from_cache
		active_queues = get_active_q_dict_from_cache(inspect=self.app.control.inspect())

		self.logger.debug("Setting active queues\n'{0}'.".format(active_queues))
		ScannerType.objects.set_active_by_q_dict(active_queues)


def get_periodic_queues():
	from kombu import Queue
	q_list = [Queue('default', routing_key='task.default'),
	        Queue(EngineActiveMarkerTask.queue, routing_key=EngineActiveMarkerTask.routing_key), 
	        Queue(RescanNonExpiredNonInfectedFiles.queue, routing_key=RescanNonExpiredNonInfectedFiles.routing_key)]
	return q_list

