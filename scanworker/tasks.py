
import sys
import traceback
import pkgutil
from celery.task import Task, PeriodicTask
from celery.utils.log import get_task_logger
from celery.app.registry import TaskRegistry
import logging
logr = logging.getLogger(__name__)
import engines
from scanworker.exception import *

# DON't import masterworker or anything from virsuscan/* here ...
# it breaks the master/worker separation where celery is concerned!


LINUX_PLATFORM = "Linux"


class EngineUpdateTask(Task):
	"""
	This is a task which updates the engine that we pass in on this box.

	The box itself is responsible for taking itself off the queue.
	"""
	
	def run(self, engine_class, update_file = None):
		e = engine_class()
		if update_file:

			return e.update_definitions(update_file)
		else:
			return e.update_definitions()


class EngineWorkerTask(Task):
	""" 
	Abstract class to source for celery tasks 
	Must define the 'name' 'class_name', and 'pkg_name' variables

	'name' is used by celery for routing
	'class_name' and 'pkg_name' is used to load the right scanner class

	Each class that inherits from this must define a celery route in celeryconfig.py
	""" 
	name 		= None
	pkg_name 	= None
	class_name 	= None
	platform 	= None
	logger 		= get_task_logger(__name__)

	def _import_scanner(self):
		"""
		Dynamically loads the scanner class
		"""
		sys.path.append("..")
		scan_class = None

		try:
			scan_mod = __import__(self.pkg_name, fromlist=[self.class_name])
			scan_class = getattr(scan_mod, self.class_name)
		except:
			self.logger.error("Error: Unable to import scanner class ({0}).".format(self.class_name))
			raise ScannerClassNotFound()

		return scan_class

	@property
	def celery_queue(self):
		from kombu import Queue
		# todo include these kwargs below and figure out how to get them into the task as well auto_delete= True, queue_arguments={"x-message-ttl": 60000}
		qname = self._import_scanner()().q_name
		self.logger.debug("Got celery queue: '{0}'.".format(qname))
		return Queue(qname, routing_key=qname, auto_delete=True, queue_arguments={"x-message-ttl": 60000 * 60})

	@classmethod
	def get_scanner_adapter_class(cls):
		return cls()._import_scanner()

	def _scan_file(self, f):
		"""
		Runs the scanner
		"""
		scanner = self._import_scanner()
		s = scanner()

		if not s.is_installed():
			raise ScannerIsNotInstalled()
		self.logger.debug("scanning file: '{0}'.".format(f))
		return s.scan(f)

	def _declare_queue(self):
		q_obj = self.celery_queue
		self.logger.debug("declaring celery queue for '{0}'.".format(q_obj.name))
		self.app.amqp.queues.add(q_obj)

	@classmethod
	def declare_celery_queue(cls, care_about_install=False):
		ec = cls()
		if care_about_install:
			if ec._import_scanner()().is_installed():
				ec._declare_queue()
		else:
			ec._declare_queue()

	def run(self, f): 
		""" 
		Receives and runs a task 
		"""
		return self._scan_file(f)


# ref: http://aleatory.clientsideweb.net/2012/04/03/how-to-introspect-dynamically-create-classes-in-python/
# ref: http://stackoverflow.com/questions/3915024/dynamically-creating-classes-python
class GenericScanners:
	def _valid_scanner_check_filter(self, engine_task_class):
		try:
			self._check_engine_installed(engine_task_class)
			return True

		except ScannerIsNotInstalled:
			return False

		except:
			logr.error("Unhandled exception on valid scanner check for {0}.".format(engine_task_class.__name__))
			logr.error(traceback.print_exc())

	def _os_compat_ok_filter(self, engine_task_class):
		return engine_task_class.get_scanner_adapter_class().os_compatibility()

	def _package_list(self):
		return list(pkgutil.iter_modules(engines.__path__))

	def _import_scanner_class(self, pkg_name, class_name):
		return __import__(pkg_name, fromlist=[class_name])

	def _check_engine_installed(self, engine_task_class):
		scanner_adapter_class = engine_task_class.get_scanner_adapter_class()
		engine_installed = scanner_adapter_class().is_installed()
		engine_installed_str = ("NOT INSTALLED", "installed")[engine_installed == True]
		msg = "Found adapter for '{0}'.".format(scanner_adapter_class.__name__)		
		logr.info("{0}{1}{2}".format(msg, '.' * (60 - len(msg) - len(engine_installed_str)), engine_installed_str))
		if not engine_installed:
			raise ScannerIsNotInstalled()

	def _internal_iter(self):
		for importer, engine_name, ispkg in self._package_list():
			# skip the 'generic' engine
			if 'generic' == engine_name: continue

			pkg_name 	= 'engines.{0}.scanner'.format(engine_name)
			class_name	= '{0}_engine'.format(engine_name)
			try:
				# determine if the engine should be enabled (is it properly "installed"?)
				imported_scanner_class = self._import_scanner_class(pkg_name, class_name)

				# define the new class
				engine_class = type(engine_name, (EngineWorkerTask, ), {
					'pkg_name' 		: pkg_name,
					'class_name' 	: class_name,
					'name'			: 'scanworker.tasks.{0}'.format(engine_name),
					# todo: make this dynamic
					'platform' 		: LINUX_PLATFORM,
					# routing key and queue must be put in here or else celery will fail
					'queue'         : engine_name,
					'routing_key' 	: engine_name,
				})
				# found engines that are "installed" are added to the following lists
				# this is important to get the x-message-timeout property on all queues
				yield engine_class

			except:
				# todo: protect against the scanners throwing exceptions and breaking the whole import process
				logr.error("Unhandled exception")
				logr.error(traceback.print_exc())

	@property
	def names(self):
		for engine_class in self:
			yield engine_class.__name__

	def celery_virus_scan_routes(self):
		for scanner, q_name in zip(self, self.names):
			route_key = scanner.name
			queue = q_name
			routing_key = queue
			inner_dict = {
				'queue': queue,
				'routing_key': routing_key,
			}
			yield (route_key, inner_dict)

	def celery_virus_scan_queues(self):
		vsqs = [s().celery_queue for s in self]

		return vsqs

	def _make_part_of_task_package(self, engine_task_class):
		# add new class as child of this package (scanworker.tasks)
		# a.k.a. realize engine_class.name, so that we can do stuff like "from scanworker.tasks import officemalscanner"
		setattr(sys.modules[__name__], engine_task_class.__name__, engine_task_class)

	def create_all_scan_tasks(self):
		# this should not declare queues too! take care when changing
		map(self._make_part_of_task_package, self._internal_iter())


class VALID_SCANNERS_NO_INSTALL_CHECK(GenericScanners):
	care_about_install = False

	def __iter__(self):
		for scanner in self._internal_iter():
			scanner.declare_celery_queue()
			yield scanner

	def __len__(self):
		return len(list(self.__iter__()))


class VALID_SCANNERS(GenericScanners):

	care_about_install = True

	def tasks_no_install(self):
		tr = TaskRegistry()
		map(tr.register, self._internal_iter())
		from scanworker.masterworker import MasterWorkerTask
		tr.register(MasterWorkerTask)

		from scanworker.result import ScanRunResultHandlerTask, ScanRunErrorHandlerTask, ScanRunFinalizerTask
		map(tr.register, [ScanRunErrorHandlerTask, ScanRunResultHandlerTask, ScanRunFinalizerTask, EngineUpdateTask])
		return tr

	def __iter__(self):
		for checked_scanner in self.installed_engines:
			self._make_part_of_task_package(checked_scanner)
			checked_scanner.declare_celery_queue()
			yield checked_scanner

	@property
	def celery_virus_scan_queues_install_check(self):
		return [scanner_engine().celery_queue for scanner_engine in self.installed_engines]

	@property
	def installed_engines(self):
		for installed_engine in filter(self._os_compat_ok_filter,
		                               filter(self._valid_scanner_check_filter, self._internal_iter())):
			yield installed_engine


VALID_SCANNERS_NO_INSTALL_CHECK().create_all_scan_tasks()

