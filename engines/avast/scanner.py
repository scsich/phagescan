
import os
from engines.generic.abstract import AbstractEvilnessEngine, L32_PLATFORM
from engines.generic.exception import UnsupportedFileTypeForScanner, ScannerUpdateError
from subprocess import check_output, CalledProcessError
import tempfile


class avast_engine(AbstractEvilnessEngine):
	# this flag indicates whether we require a file from the master
	_requires_update_file_from_master = False

	def __init__(self, engine_path='/opt/avast/bin/avastcmd', update_engine='/usr/bin/avastvpsupdate.sh'):
		super(avast_engine, self).__init__()
		self._engine_path = engine_path
		self._update_engine = update_engine
		self._name = 'Avast'
		self._platform = L32_PLATFORM

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		'definitions': virus definitions file version
		"""

		# The --version flag gives us output like the following:
		# avast: avast v1.3.0
		# VPS: 121018-2 (date: 18.10.2012)
		# ...

		# avast! will nonzero on success (really).  This will cause a CalledProcessError exception to be thrown.
		vers = ''
		try:
			vers = check_output([self._engine_path, '--version'])
		except CalledProcessError, e:
			vers = e.output.split('\n')

		engineVers	= vers[0].split()[-1][1:]
		defsVers	= vers[1][len('VPS: '):]
		return {'engine': engineVers, 'definitions': defsVers}

	def is_installed(self):
		if not self.engine_path_exists() or not self.is_engine_path_executable():
			return False

		# use version() function to determine if correct libs are installed and Avast! is responding correctly
		try:
			tmp = self.version
		# this exception will get thrown when execution attempt on x86_64 absent necessary 32-bit libs
		except OSError as e:
			return False
		# this exception will get thrown if self.version gives output 
		# in an invalid format (probably meaning it's not installed)
		except IndexError:
			return False

		return True

	def update_definitions(self):
		"""
		Run $ sudo /usr/bin/avastvpsupdate.sh to update the VPS definitions.
		It has to be run with root privs (sudo).

		Example output:
		$ sudo /usr/bin//avastvpsupdate.sh
		[sudo] password for avuser:

		ERROR-0: New VPS: 130808-0 (date: 08.08.2013) succesfully installed.
		"""

		try:
			check_output(['sudo',self._update_engine])
		except CalledProcessError, e:
			raise ScannerUpdateError(e.output.split('\n'))

	def _scan(self, file_object):

		tmpDir = tempfile.mkdtemp()
		self.samplePath = os.path.join(tmpDir, "sample")
		self.mark_path_for_removal(tmpDir)

		with open(self.samplePath, "wb") as fhSample:
			fhSample.write(file_object.all_content)

		# avast! will nonzero on success (really).  This will cause a CalledProcessError exception to be thrown.
		try:
			return check_output([self._engine_path, '--nostats', self.samplePath])
		except CalledProcessError, e:
			return e.output

	def _parse_scan_result(self, scan_result):

		# The --nostats flag strips out virtually all the fluff. Sample:
		# $ avast --nostats /tmp/file
		# /tmp/file/blat.ex_	[OK]
		# /tmp/file/eicar.com.txt	[infected by: EICAR Test-NOT virus!!!]
		# In our case, there should only be one output line.
		infected, infected_string, metadata = True, '(UNKNOWN)', dict()
		metadata.update(self.version)
		# need the original sample path in case this is a nested file with a bunch of archive members
		# TODO: find out if the overall file will be considered bad if internal OLE objects are infected ... need infected PPT
		sample_path_start = self.samplePath+'\t['
		startIdx = scan_result.find(sample_path_start)+len(sample_path_start)
		if 'infected by: ' == scan_result[startIdx:startIdx + len('infected by: ')]:
			startIdx += len('infected by: ')

		endIdx = scan_result.find(']', startIdx)
		infected_string = scan_result[startIdx:endIdx]

		if 'OK' == infected_string:
			infected = False
			infected_string = ''

		# this will produce a "Scan Failed" UI result.  this is by design because Avast is literally failing.
		elif 'scan error: Archive is corrupted' == infected_string:
			raise UnsupportedFileTypeForScanner

		return infected, infected_string, metadata
