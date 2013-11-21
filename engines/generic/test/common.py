
from engines.generic.abstract import AbstractEvilnessEngine, L32_PLATFORM
from scanworker.file import PickleableFileSample
from nose.tools import ok_, eq_
import hashlib
import os


EICAR_MD5_HEX		= '44d88612fea8a8f36de82e1278abb02f'
EICAR_SHA256_HEX	= '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
TEST_FILE_DIR_PATH = os.path.join(os.path.dirname(__file__), 'file')
EICAR_TEST_FILE_PATH = os.path.join(TEST_FILE_DIR_PATH, 'eicar.com.txt')
EVIL_PDF_TEST_FILE = os.path.join(TEST_FILE_DIR_PATH, 'evil.pdf')
INERT_FILE_PATH = os.path.join(TEST_FILE_DIR_PATH , 'blat.ex_')
EVIL_PDF_MD5_HEX = 'db3527797767c2f5ffbd737d26d6c78b'
CLEAN_TEST_FILE_PATH = os.path.dirname(__file__) + '/file/blat.ex_'


class FakeEicarOnlyScannerAdapter(AbstractEvilnessEngine):
	_name =  'FakeScanner'
	_platform = L32_PLATFORM
	_engine_path = 'fake/scanner/path'

	@property
	def version(self):
		return "1"

	@property
	def is_installed(self):
		return True

	@property
	def scannerPath(self):
		return self._engine_path

	def _parse_scan_result(self, scan_result):
		return scan_result, 'Eicar' if scan_result else '', {}

	def _scan(self, file_object):
		return hashlib.sha256(file_object.all_content).hexdigest() == EICAR_SHA256_HEX


class EngineTemplate(object):

	# must be overridden
	scan_class = None

	@property
	def scanner(self):
		if not hasattr(self, '_scanner'):
			self._scanner = self.scan_class()
		return self._scanner

	def _null_scan_check(self, scan_result):
		ok_(scan_result, msg="Non-existent scan_result")

	def _ensure_true_positive(self, scan_result):
		self._null_scan_check(scan_result)
		ok_(scan_result.infected, msg="Should have an infected scan for 'evil' sample")
		eq_(scan_result.infected_string, self.infected_string, msg="Should have an infected_string for 'evil' sample")

	def _ensure_true_negative(self, scan_result):
		self._null_scan_check(scan_result)
		ok_(not scan_result.infected, msg="Scan result was marked infected and shouldn't have been")
		eq_(scan_result.infected_string, '', msg="Infection string should have been of 0 len")

	def test_name(self):
		"""
		Querying scanner's name, (e.g. 'Avast')
		"""
		ok_(len(self.scanner.name) > 0)

	def test_platform(self):
		"""
		Querying scanner's platform, (e.g. 'Linux 32')
		"""
		ok_(len(self.scanner.platform) > 0)

	def test_engine_path_exists(self):
		"""
		Checking whether the scanner's control binary exists
		"""
		eq_(True, self.scanner.engine_path_exists())

	def test_engine_path_executable(self):
		"""
		Checking whether the scanner's control binary is executable
		"""
		eq_(True, self.scanner.is_engine_path_executable())

	def test_engine_installed(self):
		"""
		Checking whether a valid license file is present (no-op for scanners that don't require a license)
		"""
		eq_(True, self.scanner.is_installed())

	def test_license_installed(self):
		"""
		Checking whether a valid license file is present (no-op for scanners that don't require a license)
		"""
		eq_(True, self.scanner.is_engine_licensed())

	def test_version(self):
		"""
		Checking for a valid version string
		"""
		ok_(self.scanner.version != {})


class EvilnessEngineTemplate(EngineTemplate):
	"""
	A subset of engines that attempt to determine "evilness" of a given sample.  These engines produce a "malicious" or
	"benign" indication
	"""

	# must be overrridden
	evil_file_object = None
	good_file_object = None

	def test_evil_scan(self):
		"""
		Running scanner against an evil/malicious file.  Expects scanner to categorize file as malicious
		"""
		scan_result = self.scanner.scan(self.evil_file_object)
		self._ensure_true_positive(scan_result)
		self.scanner.remove_generated_files()

	def test_good_scan(self):
		"""
		Running scanner against a good/benign file.  Expects scanner to categorize file as innocent
		"""
		self._null_scan_check(self.scanner.scan(self.good_file_object))
		self.scanner.remove_generated_files()
		# todo: add call to _ensure_true_negative here?


class PickyEngineTemplate(EngineTemplate):
	"""
	A subset of engines that exhibit "picky" characteristics.  They only support certain filetypes
	"""
	unsupported_string = 'Unsupported'

	# must be overrridden
	supported_file_object = None
	unsupported_file_object = None

	def _ensure_unsupported(self, scan_result):
		self._null_scan_check(scan_result)
		ok_(scan_result.infected,
			msg="Should have an 'Unsupported' scan for 'unsupported' sample")
		eq_(scan_result.unsupported_string,
			self.unsupported_string,
			msg="Should have an 'Unsupported' scan for 'unsupported' sample")

	def test_unsupported_scan(self):
		"""
		Running scanner against an unsupported file.  Does not expect parse results
		"""

		# if the file is not supported by the scanner, the scanner must throw a UnsupportedFileTypeForScanner
		# if it does, it passes this test, otherwise it fails
		# todo: add call to _ensure_true_negative here?
		self._null_scan_check(self.scanner.scan(self.unsupported_file_object))
		self.scanner.remove_generated_files()

	def test_supported_scan(self):
		"""
		Running scanner against a supported file. Expects parse results
		"""
		# todo: add call to _ensure_true_negative here?
		self._null_scan_check(self.scanner.scan(self.supported_file_object))
		self.scanner.remove_generated_files()


class AVEngineTemplate(EvilnessEngineTemplate):

	def setUp(self):
		self.evil_file_object = _make_eicar_picklable_file_object()
		self.good_file_object = _make_inert_file_object_small()


def _make_eicar_picklable_file_object():

	return PickleableFileSample.path_factory(EICAR_TEST_FILE_PATH)


def _make_inert_file_object_small():

	return PickleableFileSample.path_factory(INERT_FILE_PATH)
