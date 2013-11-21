
import os
import sys
import re
import shutil
import logging
logr = logging.getLogger(__name__)
# todo does this import break our new deploy strategy
from scanworker.file import PickleableFileSample
from engines.generic.exception import ScannerRequiresLicenseFile
from engines.generic.result import GenericEvilnessResult, GenericMDResult

L64_PLATFORM = 'L64'
L32_PLATFORM = 'L32'
W64_PLATFORM = 'W64'
W32_PLATFORM = 'W32'

PLATFORM_CHOICES = (
	(W32_PLATFORM, 'Windows 32'),
	(W64_PLATFORM, 'Windows 64'),
	(L32_PLATFORM, 'Linux 32'),
	(L64_PLATFORM, 'Linux 64')
)


class EngineNotExecutable(Exception):
	pass


class FileNotFoundInPath(Exception):
	pass


class PathNotAbsolute(Exception):
	pass


class AbstractEngine(object):

	def __init__(self):

		# must be overridden
		self._name = None
		self._platform = None
		self._engine_path = None
		self._files_to_remove = set()
		self._supported_file_types = [r'.*'] # default to all, subclass to restrict

	@classmethod
	def os_compatibility(cls):
		# default to compatible on linux, over-ride if not
		return sys.platform == 'linux2' # this is not a typo of "linux32"

	def _check_full_path_or_except(self, path):
		if os.path.isabs(path):
			return
		raise PathNotAbsolute

	@property
	def name(self):
		"""
		Name of scanner
		"""
		return self._name

	@property
	def q_name(self):
		return self.__class__.__name__.split("_")[0]


	@property
	def platform(self):
		'''
		OS Platform we're running on
		'''
		return self._platform

	@property
	def requires_update_file_from_master(self):
		return getattr(self, '_requires_update_file_from_master', False)

	@property
	def engine_path(self):
		return self._engine_path

	@property
	def supported_file_types(self):
		return self._supported_file_types

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		'definitions': virus definitions file version
		"""
		raise NotImplementedError

	def _scan(self, file_object):
		"""
		Must-override method to perform the scan

		Must result in a returned triple: infected (boolean), infected string (non '' if file infected), scan_metadata (dict for now)
		"""
		raise NotImplementedError

	def _parse_scan_result(self, scan_result):
		"""
		Must-override method to parse the output of the scan below

		Must result in a returned triple: infected (boolean), infected string (non '' if file infected), scan_metadata (dict for now)
		"""
		raise NotImplementedError

	# TODO: Make so this can return a NotImplementedError.
	# TODO: Implement in each engine and cache the result so we don't have to repeatedly shell out to check for the license.
	def is_engine_licensed(self):
		"""
		Returns boolean indicating whether the scanner has a license file installed.  This function is intended to be
		overrridden by extending classes.  As not all scanners require a license file, we default this to True.
		"""
		return True

	def engine_path_exists(self):
		if self._engine_path is None: return True # not all scanners require an engine path
		exists = self._path_exists(self._engine_path)
		logr.debug("Engine path existance is: {0}.".format(exists))
		return exists

	def is_engine_path_executable(self):
		if self._engine_path is None: return True # not all scanners require an engine path
		if os.path.isfile(self._engine_path) and os.access(self._engine_path, os.X_OK):
			logr.debug("Engine path '{0}' is execuatable.".format(self._engine_path))
			return True
		logr.debug("Engine path '{0}' is not execuatable.".format(self._engine_path))
		return False

	def is_installed(self):
		"""
		Returns boolean indicated whether all files and settings are configured for successful usage of the engine.
		This should be overridden by subclasses and given more stringent checks.
		"""
		logr.debug("Checking if engine {0} is installed.".format(self._name))
		return self.engine_path_exists() and self.is_engine_path_executable() and self.is_engine_licensed()

	def _get_abs_which(self, file_sample, include_virt_env=True):

		paths = os.environ["PATH"].split(os.pathsep)

		# there is no virtual environment variable set in test setups so refs to virtualenv fail ...
		# instead refer to python interp in virtual env directly
		if include_virt_env:
			paths = [os.path.dirname(sys.executable)] + paths

		for path in paths:
			guess = os.path.join(path, file_sample)
			if self._path_exists(guess):
				return guess

		raise FileNotFoundInPath()

	def _path_exists(self, path):
		if not os.path.isabs(path):
			try:
				path = self._get_abs_which(path)
			except FileNotFoundInPath:
				return False

		# avoids race condition
		# ref: http://stackoverflow.com/questions/82831/how-do-i-check-if-a-file-exists-using-python
		if os.path.isfile(path):
			try:
				with open(path) as f:
					return True
			except IOError as e:
				return False
		return False

	def scan(self, file_object):
		if not self.is_engine_licensed():
			raise ScannerRequiresLicenseFile
		return self.do_scan(file_object)

	def do_scan(self, file_object):
		raise NotImplementedError

	def mark_path_for_removal(self, path):
		"""
		Inform the scan adapter that you have generated a file on disk that needs to be removed after the results
		are shipped off.

		This does not add it to output or anything else so can be used for temp files that you don't need anymore
		"""
		self._check_full_path_or_except(path)
		self._files_to_remove.add(path)

	def remove_generated_files(self):
		"""
		Called after every scan on the worker.

		You should not over-ride this method unless your scanner is super-special.
		Instead, you should add the filepaths that your scanner outputs according to the following:

		* Intermediate results that aren't saved (eg parsed and thrown into metadata):
			call self.mark_file_for_removal() with the abs path of the file
		* Files that need to be saved (AbstractMDEngine only):
			call self.add_output_file()
		* Images that need to be saved (AbstractMDEngine only):
			call self.add_output_image()

		"""
		for path in self._files_to_remove:
			# todo more checks on this for safety when deleting files
			if os.path.isabs(path): # the engine must have specified an absolute path
				if os.path.isfile(path):
					os.remove(path)
				elif os.path.isdir(path):
					shutil.rmtree(path)

	def get_update_file_factory(self):
		"""
		Returns a function which can generate the requisite update files on master
		"""
		raise NotImplementedError

	def update_definitions(self, *args):
		"""
		Performs update on engine signature/rules definitions.

		Raises ScannerUpdateError if update doesn't complete as expected.
		"""
		raise NotImplementedError


class AbstractEvilnessEngine(AbstractEngine):
	"""
	A superset of AV engines, Evilness encompasses all engines that provide a "benign" / "evil" determination
	"""
	ENGINE_VERSION_KEY = "engine"
	DEFINITION_VERSION_KEY = "definitions"

	def do_scan(self, file_object):
		"""
		Generic method for scanning a sample

		:parameter  PickleableFileSample file_object
		:returns: GenericScanResult - a python object containing a minimum of a file digest (sha256), boolean indicating infection, and an infection string (default '')
		"""
		# todo: check that file object is a correct instance of PickleableFileSample

		# todo: provide generic exceptions for scan failures

		infected, infected_string, metadata = self._parse_scan_result(self._scan(file_object))
		parsed_scan_object = GenericEvilnessResult(file_object.digest, infected=infected, infected_string=infected_string, metadata=metadata)
		self.remove_generated_files()
		return parsed_scan_object


class AbstractMDEngine(AbstractEngine):
	"""
	A superset of engines where MD means metadata. These engines provide metadata about a sample.
	"""
	def __init__(self):
		super(AbstractMDEngine, self).__init__()
		self._output_files = set()
		self._output_images = set()

	def add_output_file(self, path, mark_for_removal=True):
		"""
		Add file for scanresult output and ensture its an absolute path.
		"""
		if mark_for_removal: self.mark_path_for_removal(path)
		self._output_files.add(path)

	def add_output_file_from_string(self, string_buffer, original_filename = None):
		"""
		Add an output file but do it all in memory from a string buffer, no removal required
		"""
		self._output_files.add(PickleableFileSample.string_factory( string_buffer, original_filename=original_filename))

	def add_output_image(self, path, mark_for_removal=True):
		"""
		Add an image for output, ensure its an absolute path (based on tempdir). Also, automatically
		add if for removal after its shipped off to the database.

		Use this to notify the MD engine that it needs to return some image that the scanner produces for storage
		in the django database.
		"""
		if mark_for_removal: self.mark_path_for_removal(path)
		self._output_images.add(path)

	def do_scan(self, file_object):
		"""
		Generic method for scanning a file from a metadata perspective

		:parameter  PickleableFileSample file_object
		:returns: MDScanResult - a python object containing a minimum of a file digest (sha256),
		"""
		# todo check that file_object is a correct instance of PickleableFileSample

		# call scan method defined in concrete implementation
		files, images, metadata = self._parse_scan_result(self._scan(file_object))
		parsed_scan_object = GenericMDResult(file_object.digest, files=files, images=images, metadata=metadata)
		self.remove_generated_files()
		return parsed_scan_object
