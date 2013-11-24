
from celery.task import Task
from celery.result import AsyncResult
from virusscan.models import ScanRunResult, ScanRun
from celery.utils.log import get_task_logger


class ScanRunErrorHandlerTask(Task):
	queue = 'ScanRunErrorHandlerTask'
	routing_key =  queue
	ignore_result = True
	logger = get_task_logger(__name__)

	def run(self, task_id):
		# we know its an exception because we're on a link back
		self.logger.debug("Running ScanRunErrorHandlerTask.")
		exc = AsyncResult(task_id)
		sr_update = ScanRunResult.objects.filter(task_id=task_id).update(pending=False, traceback=exc.traceback)


class ScanRunResultHandlerTask(Task):
	queue = 'ScanRunResultHandlerTask'
	routing_key = queue
	ignore_result = True
	logger = get_task_logger(__name__)

	def run(self, generic_evil_result, task_id):
		self.logger.debug("Starting scanrun task '{0}'.".format(task_id))
		scan_run = ScanRun.objects.get(scanrunresult__task_id=task_id)
		scan_run.mark_started()

		result = AsyncResult(task_id)
		self.logger.debug("Populating scanrun results for task '{0}'.".format(task_id))
		scan_run.populate_scan_run_result_from_scanner(result)
		# todo mark the scan run as a success if we're the last one in


class ScanRunFinalizerTask(Task):
	queue = 'ScanRunFinalizerTask'
	routing_key = queue
	ignore_result = True
	logger = get_task_logger(__name__)

	def run(self, scan_run):
		# this thing's job is to finalize the scan run
		self.logger.debug("Finalizing scanrun.")
		scan_run.check_tasks_and_mark_finished()


def get_result_saver_queues():
	from kombu import Queue
	q_list = [Queue('default', routing_key='task.default'),
	        Queue(ScanRunFinalizerTask.queue, routing_key=ScanRunFinalizerTask.routing_key),
	        Queue(ScanRunErrorHandlerTask.queue, routing_key=ScanRunErrorHandlerTask.routing_key),
	        Queue(ScanRunResultHandlerTask.queue, routing_key=ScanRunResultHandlerTask.routing_key)]
	return q_list

