
import os
import unittest
from nose.tools import ok_
from engines.peid.scanner import peid_engine
from engines.generic.test.common import PickyEngineTemplate
from engines.generic.exception import UnsupportedFileTypeForScanner
from scanworker.file import PickleableFileSample


class TestPEIDEngine(PickyEngineTemplate, unittest.TestCase):

	scan_class = peid_engine

	def setUp(self):
		TEST_FILE_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'generic', 'test', 'file')
		self.supported_file_object = PickleableFileSample.path_factory(os.path.join(TEST_FILE_DIR_PATH, 'blat.ex_'))
		self.unsupported_file_object = PickleableFileSample.path_factory(os.path.join(TEST_FILE_DIR_PATH, 'evil.pdf'))

	def test_supported_scan(self):
		"""
		Running scanner against a supported file (.exe).  Expecting parse results
		"""
		my_peid_engine = peid_engine()
		TEST_FILE_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'generic', 'test', 'file')
		path = PickleableFileSample.path_factory(os.path.join(TEST_FILE_DIR_PATH, 'blat.ex_'))
		my_scan = my_peid_engine.scan(path)

	def test_unsupported_scan(self):
		"""
		Running scanner against an unsupported file (.pdf).  Not expecting parse results
		"""
		my_peid_engine = peid_engine()
		TEST_FILE_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'generic', 'test', 'file')
		path = PickleableFileSample.path_factory(os.path.join(TEST_FILE_DIR_PATH, 'evil.pdf'))
		try:
			my_scan = my_peid_engine.scan(path)
			ok_(False)
		except UnsupportedFileTypeForScanner:
			ok_(True)