
from celery.task import Task
from celery.utils.log import get_task_logger


class MasterWorkerTask(Task):
	"""
	Master worker task which can handle multiple scanworker tasks FOR A SINGLE SAMPLE

	Several of these master worker tasks can operate at any time because they're operating on separate samples
	"""
	name = "scanworker.masterworker.MasterWorkerTask"
	queue = 'MasterWorkerTask'
	routing_key = 'MasterWorkerTask'
	logger = get_task_logger(__name__)
	track_started = True

	def run(self, sample):
		"""
		Execute this task

		Params FileSample (sample), scanners = an iterable
		"""
		from django import db
		db.close_connection()
		self.logger.debug("Launching all scanning subtasks for sample.")
		sample._launch_all_scanning_subtasks()


def generate_celery_mastertask_queue():
	from kombu import Queue

	return [Queue(MasterWorkerTask.queue, routing_key=MasterWorkerTask.routing_key),
			Queue('default', routing_key='task.default'),
			Queue("RescanNonExpiredNonInfectedFiles", routing_key="task.default")]
