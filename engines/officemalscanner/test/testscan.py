
import unittest
from os.path import dirname, join
from engines.officemalscanner.scanner import officemalscanner_engine
from engines.generic.test.common import PickyEngineTemplate, EvilnessEngineTemplate
from scanworker.file import PickleableFileSample


class TestOMSEngine(PickyEngineTemplate, EvilnessEngineTemplate, unittest.TestCase):

	scan_class = officemalscanner_engine

	# concat the results of 'scan' and 'info' flags
	infected_string = 'Malicious Index = 10'

	def setUp(self):
		TEST_FILE_DIR_PATH 			 	= join(dirname(__file__), 'file')
		self.evil_file_object 		 	= PickleableFileSample.path_factory(join(TEST_FILE_DIR_PATH, 'SAMPLE.evil'))
		self.good_file_object 			= PickleableFileSample.path_factory(join(TEST_FILE_DIR_PATH, 'SAMPLE.good'))
		self.supported_file_object		= PickleableFileSample.path_factory(join(TEST_FILE_DIR_PATH, 'SAMPLE.good'))
		self.unsupported_file_object	= PickleableFileSample.path_factory(join(TEST_FILE_DIR_PATH, 'SAMPLE.unsupported'))
