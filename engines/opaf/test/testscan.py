
import unittest
from nose.tools import ok_
from os.path import dirname
from engines.generic.exception import UnsupportedFileTypeForScanner
from engines.opaf.scanner import opaf_engine
from engines.generic.test.common import PickyEngineTemplate
from scanworker.file import PickleableFileSample


class TestOPAFEngine(PickyEngineTemplate, unittest.TestCase):
    scan_class = opaf_engine

    def setUp(self):
        TEST_FILE_DIR_PATH = dirname(__file__) + '/file'
        self.supported_file_object = PickleableFileSample.path_factory(TEST_FILE_DIR_PATH + '/SAMPLE.good')
        self.unsupported_file_object = PickleableFileSample.path_factory(TEST_FILE_DIR_PATH + '/SAMPLE.unsupported')

    def test_unsupported_scan(self):
        try:
            self.scanner.scan(self.unsupported_file_object)
            ok_(False)
        except UnsupportedFileTypeForScanner as e:
            ok_(True)


class TestOPAFEngineJS(PickyEngineTemplate, unittest.TestCase):
    scan_class = opaf_engine

    def setUp(self):
        TEST_FILE_DIR_PATH = dirname(__file__) + '/file'
        self.supported_file_object = PickleableFileSample.path_factory(TEST_FILE_DIR_PATH + '/SAMPLE.good')
        self.unsupported_file_object = PickleableFileSample.path_factory(TEST_FILE_DIR_PATH + '/SAMPLE.evil_javascript')
