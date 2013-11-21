import atexit
from celery.app.control import flatten_reply
from celery.app import Celery
from celery.exceptions import TimeoutError
from celery.utils.imports import qualname
from itertools import count
import os
import signal
import socket
import sys
from time import time
import traceback


def _get_current_app(config_mod):
	current_app = Celery(config_source=config_mod,
	                     include=config_mod.CELERY_IMPORTS,
	                     tasks=config_mod.VALID_SCANNERS.tasks_no_install())
	return current_app


def say(msg):
	sys.stderr.write('%s\n' % msg)


def try_while(fun, reason='Timed out', timeout=10, interval=0.5):
	time_start = time()
	for iterations in count(0):
		if time() - time_start >= timeout:
			raise TimeoutError()
		ret = fun()
		if ret:
			return ret


def _post_fork():
	print "Closing django connection post fork."
	from django import db
	db.connection.close()


class Worker(object):
	started = False
	next_worker_id = count(1).next
	_shutdown_called = False

	@property
	def config_module(self):
		import dev.dev_worker as test_app_config
		return test_app_config

	def __init__(self, hostname, loglevel='error'):
		self.hostname = hostname
		self.loglevel = loglevel

	def start(self):
		if not self.started:
			self._fork_and_exec()
			self.started = True

	def _fork_and_exec(self):
		_post_fork()
		pid = os.fork()

		if pid == 0:
			# special to make sure we pick up our dev config

			ca = _get_current_app(self.config_module)
			ca.control.purge()

			ca.worker_main(['celeryd',
			                '--loglevel=INFO',
			                '-n', self.hostname,
			                '--workdir', os.path.abspath(os.path.join(os.path.dirname(__file__), '../')),
			                ])
			os._exit(0)

		self.pid = pid

	def is_alive(self, timeout=1):
		try:
			r = _get_current_app(self.config_module).control.ping(destination=[self.hostname], timeout=timeout)
			return self.hostname in flatten_reply(r)
		except IOError:
			# were not up yet...
			return False

	def wait_until_started(self, timeout=10, interval=0.5):
		try_while(
			lambda: self.is_alive(interval),
			"Worker won't start (after {0} secs.).".format(timeout),
			interval=interval, timeout=timeout,
		)
		say('--WORKER {0} IS ONLINE--'.format(self.hostname))

	def ensure_shutdown(self, timeout=10, interval=0.5):
		os.kill(self.pid, signal.SIGTERM)
		try_while(
			lambda: not self.is_alive(interval),
			"Worker won't shutdown (after {0} secs.).".format(timeout),
			timeout=10, interval=0.5,
		)
		say('--WORKER {0} IS SHUTDOWN--'.format(self.hostname))
		self._shutdown_called = True

	def ensure_started(self):
		self.start()
		self.wait_until_started()

	@classmethod
	def managed(cls, hostname=None, caller=None):
		hostname = hostname or socket.gethostname()
		if caller:
			hostname = '.'.join([qualname(caller), hostname])
		else:
			hostname += str(cls.next_worker_id())
		worker = cls(hostname)
		worker.ensure_started()
		stack = traceback.format_stack()

		@atexit.register
		def _ensure_shutdown_once():
			if not worker._shutdown_called:
				say('-- Found worker not stopped at shutdown: %s\n%s' % (
				worker.hostname,
				'\n'.join(stack)))
				worker.ensure_shutdown()

		return worker


class Master(Worker):
	def _fork_and_exec(self):
		_post_fork()
		pid = os.fork()

		if pid == 0:
			# special to make sure we pick up our dev config
			ca = _get_current_app(self.config_module)
			ca.control.purge()
			ca.worker_main(['celeryd',
			                '--loglevel=INFO',
			                '-n', self.hostname,
			                '--workdir', os.path.abspath(os.path.join(os.path.dirname(__file__), '../')),
			                ])
			os._exit(0)

		self.pid = pid

	@property
	def config_module(self):
		import dev.dev_master as test_app_config
		# otherwise celeryd won't know we're going against the test database
		test_app_config.DATABASES['default']['NAME'] = "test_{0}".format(test_app_config.DATABASES['default']['NAME'])
		return test_app_config

	def ensure_started(self):

		self.hostname = "{0}_master".format(self.hostname)
		super(Master, self).ensure_started()


class ResultSaver(Worker):

	def _fork_and_exec(self):
		_post_fork()
		pid = os.fork()

		if pid == 0:
			# special to make sure we pick up our dev config

			ca = _get_current_app(self.config_module)
			ca.control.purge()
			ca.worker_main(['celeryd',
			                '--loglevel=INFO',
			                '-n', self.hostname,
			                '--workdir', os.path.abspath(os.path.join(os.path.dirname(__file__), '../')),
			                ])
			os._exit(0)

		self.pid = pid
	@property
	def config_module(self):
		import dev.dev_resultsaver as test_app_config
		# otherwise celeryd won't know we're going against the test database
		test_app_config.DATABASES['default']['NAME'] = "test_{0}".format(test_app_config.DATABASES['default']['NAME'])
		return test_app_config

	def ensure_started(self):
		self.hostname = "{0}_result_saver".format(self.hostname)
		super(ResultSaver, self).ensure_started()
