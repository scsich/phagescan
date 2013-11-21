
from engines.clamav.file import pyclamd
from engines.generic.abstract import AbstractEvilnessEngine, L32_PLATFORM
from engines.generic.exception import ScannerConnectionError, ScannerUpdateError
from subprocess import check_output, CalledProcessError
import time


class clamav_engine(AbstractEvilnessEngine):
	# this flag indicates whether we require a file from the master
	_requires_update_file_from_master = False

	def __init__(self, engine_path='/usr/bin/clamscan', local_socket='/var/run/clamav/clamd.ctl', stream_key='stream'):
		super(clamav_engine, self).__init__()
		self._engine_path 	= engine_path
		self._local_socket 	= local_socket
		self._stream_key 	= stream_key
		self._name          = 'ClamAV'
		self._platform      = L32_PLATFORM

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		'definitions': virus definitions file version
		"""
		# clamscan --version gives us output like the following:
		# $ clamscan --version
		# ClamAV 0.97.6/15481/Sat Oct 20 08:43:20 2012
		vers = check_output([self._engine_path, '--version']).split('/')
		engineVers	= vers[0].split()[1]
		defsVers	= vers[1]
		return {'engine': engineVers, 'definitions': defsVers}

	def update_definitions(self):
		"""
		Run $ sudo /usr/bin/freshclam to update the virus definitions.
		It has to be run with root privs (sudo).

		Example output:
		$ sudo /usr/bin/freshclam
		[sudo] password for avuser:

		ClamAV update process started at Thu Aug  8 21:11:29 2013
		main.cvd is up to date (version: 54, sigs: 1044387, f-level: 60, builder: sven)
		daily.cld is up to date (version: 17649, sigs: 1516104, f-level: 63, builder: jesler)
		bytecode.cld is up to date (version: 217, sigs: 42, f-level: 63, builder: neo)

		This is what happens if we have a collision, and retry after a sleep:
		(psvirtualenv)vagrant@phagedev:~/phagescan$ nosetests -sv engines.clamav.test.testscan
		Checking whether the scanner's control binary exists ... ok
		Running scanner against an evil/malicious file.  Expects scanner to categorize file as malicious ... ok
		Running scanner against a good/benign file.  Expects scanner to categorize file as innocent ... ok
		Checking whether a valid license file is present (no-op for scanners that don't require a license) ... ok
		Querying scanner's name, (e.g. 'Avast') ... ok
		Querying scanner's platform, (e.g. 'Linux 32') ... ok
		Run test of A/V definition update functionality. ... ERROR: Problem with internal logger (UpdateLogFile = /var/log/clamav/freshclam.log).
		WARNING: flashclam failed to get a lock on update files.  Trying again in 30...
		ok

		----------------------------------------------------------------------
		Ran 7 tests in 31.319s

		OK
		"""
		self._update_engine = "/usr/bin/freshclam"
		self._retry_timeout = 30
		try:
			check_output(['sudo', self._update_engine])
		except CalledProcessError, e:
			# this happens if there's already a freshclam instance running; wait and try again
			if e.output.find("ERROR: /var/log/clamav/freshclam.log is locked by another process") != -1:
				print "WARNING: freshclam failed to get a lock on update files.  Trying again in {0}s...".format(self._retry_timeout)
				time.sleep(self._retry_timeout)
				try:
					check_output(['sudo', self._update_engine])
				except CalledProcessError:
					ScannerUpdateError("freshclam cannot get a lock on update files after 2 tries.")
			else:
				ScannerUpdateError(e.output.split('\n'))

	def _connect(self):
		# needed to connect to clamAV, this exception is uniform across all scanners
		if not getattr(self, '_connected', False):
			try:
				pyclamd.init_unix_socket(self._local_socket)
				self._connected = pyclamd.ping()
				assert self._connected
			except AssertionError:
				raise ScannerConnectionError

	def _scan(self, file_object):
		self._connect()
		return pyclamd.scan_stream(file_object.all_content)

	def _parse_scan_result(self, scan_result):

		infected, infected_string, metadata = False, '', dict()
		metadata.update(self.version)

		if scan_result: infected, infected_string = True, scan_result[self._stream_key].split('(')[0]

		return infected, infected_string, metadata
