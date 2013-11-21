
from subprocess import check_output, CalledProcessError
from os import write, close, path, getcwd, listdir
import tempfile
from scanworker.file import PickleableFileSample
from engines.generic.abstract import L32_PLATFORM, AbstractMDEngine


# TODO: run RTFScan.exe as well?

class officemalscanner_engine(AbstractMDEngine):

	def __init__(self, engine_path='/opt/oms/OfficeMalScanner.exe'):
		super(officemalscanner_engine, self).__init__()
		self._engine_path = engine_path
		self._name = 'OfficeMalScanner'
		self._platform = L32_PLATFORM
		self._supported_file_types = [r'application/.*excel.*',r'application/.*xls.*', 'application/.*word.*']
		self._macro_dir = None # OMS-specific

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		"""

		# $ wine OfficeMalScanner.exe
		#
		# +------------------------------------------+
		# |           OfficeMalScanner v0.56         |

		# OMS will nonzero on success (really).  
		# This will cause a CalledProcessError exception to be thrown.
		vers = ''
		try:
			check_output(['wine', self._engine_path])
		except CalledProcessError, e:
			vers = e.output
		return {'engine': vers.splitlines()[2][1:-1].strip()[len('OfficeMalScanner v'):]}

	def is_engine_path_executable(self):
		"""
		OfficeMalScanner, when run under wine, does not need to be set as executable in order to run.
		"""
		return True

	def is_installed(self):
		# oms run under wine does not need to be set as executable in order to run.
		if not self.engine_path_exists():
			return False

		# use version() function to determine if correct libs & Wine are 
		# installed and OMS is responding correctly
		try:
			tmp = self.version
		# this exception will get thrown when Wine is not installed
		except OSError:
			return False

		return True

	def _scan(self, file_object):

		(fpSample, samplePath) = tempfile.mkstemp()
		write(fpSample, file_object.all_content)
		close(fpSample)
		self.mark_path_for_removal(samplePath)

		# we want to capture 2 executions, e.g.:
		# $ wine OfficeMalScanner.exe ../test/file/SAMPLE.evil scan debug
		# $ wine OfficeMalScanner.exe ../test/file/SAMPLE.evil info
		# if OMS is run against a file that it does not consider to be an OLE2 file, the return code will be 250
		output = dict()
		tmp = ''
		try:
			tmp += check_output(['wine', self._engine_path, samplePath, 'scan', 'debug'])
		except CalledProcessError, e:
			tmp += e.output
		output['scan_debug'] = tmp

		tmp = ''
		try:
			tmp += check_output(['wine', self._engine_path, samplePath, 'info'])
		except CalledProcessError, e:
			tmp += e.output
		output['info'] = tmp

		# NOTE: OMS may extract Macros from the OLE file.  Macros are extracted to a directory under the working
		# directory. Ex: TMPISG0G3-Macros
		self._macro_dir = path.join(getcwd(), ('{0}-Macros'.format(path.split(samplePath)[1].upper())))
		self.mark_path_for_removal(self._macro_dir)
		return output

	def _parse_scan_result(self, scan_result):

		files, images, metadata = [], [], dict()
		metadata.update(self.version)

		# todo: metadata['officemalscanner'].update(scan_result)
		metadata['oms_rawresult_scan_debug'] = scan_result['scan_debug']
		metadata['oms_rawresult_info'] = scan_result['info']

		# NOTE: we are no longer concerned with detecting whether a file is "supported" or not, because we assume that
		# this engine will not be called if the MIME-type of the file does not match the _supported_file_types filter.

		# If we've gotten to this point, the file is malicious.  OMS isn't like other adapters - it's not going to give
		# you a signature name.  At best, it will give you a "malicious index".  I suppose this is as good of an
		# infection string to report as any other.
		idx_loc = scan_result['scan_debug'].find('Malicious Index = ')
		metadata['infected_string'] = scan_result['scan_debug'][idx_loc:idx_loc + len('Malicious Index = ') + 2]

		if metadata['infected_string']:
			metadata['infected'] = True
		else:
			metadata['infected'] = False

		# Loop over Macros directory, make each into Pickleable files
		if path.isdir(self._macro_dir):
			for outfile in listdir(self._macro_dir):
				files.append(PickleableFileSample.path_factory(path.join(self._macro_dir, outfile)))

		return files, images, metadata
