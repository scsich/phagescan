
import unittest
from os.path import dirname
from engines.pdfid.scanner import pdfid_engine
from engines.generic.test.common import PickyEngineTemplate
from scanworker.file import PickleableFileSample


class TestPDFIDEngine(PickyEngineTemplate,unittest.TestCase):

	scan_class = pdfid_engine

	def setUp(self):
		TEST_FILE_DIR_PATH 			 	= dirname(__file__) + '/file'
		self.supported_file_object		= PickleableFileSample.path_factory(TEST_FILE_DIR_PATH + '/SAMPLE.good')
		self.unsupported_file_object 	= PickleableFileSample.path_factory(TEST_FILE_DIR_PATH + '/SAMPLE.unsupported')







