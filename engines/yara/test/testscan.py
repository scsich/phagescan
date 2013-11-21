
import os
import unittest
from engines.yara.scanner import yara_engine
from engines.generic.test.common import AVEngineTemplate
from scanworker.file import PickleableFileSample


EICAR_TESTING_UPDATE_STRING = 'eicar_testing_update'


class CommonYaraHelpers:
	test_rule_dir = os.path.join(os.path.dirname(__file__), 'file', 'rules')
	update_tar_file = os.path.join(os.path.dirname(__file__), 'file', 'test_update.tar')
	expected_yara_files_in_update = ['infected/eicarupdatetest.yara', 'GeorBotBinary.yara',
	                                 'GeorBotMemory.yara', 'apt1.yara']

	def _remove_repo_dir(self):
		self.scanner._clear_repo_dir()

	def _clear_rule_dir(self):
		self.scanner._clear_rule.dir()


# todo test that we get ALL infection strings with the EICAR update
class TestYaraAV(CommonYaraHelpers, AVEngineTemplate, unittest.TestCase):
	scan_class = yara_engine
	infected_string = 'eicar_testing_update'
	# have to manually define scanner as having the test rules dir
	_scanner = yara_engine(rules_dir=CommonYaraHelpers.test_rule_dir)

	def setUp(self):
		self.update_tar = PickleableFileSample.path_factory(self.update_tar_file)
		AVEngineTemplate.setUp(self)
		# we have to do this once at the start to make sure all tests that rely on these rule updates run

		self._clear_rule_dir_and_update()

	def _clear_rule_dir_and_update(self):
		self.scanner._clear_rule_dir()
		self.scanner.update_definitions(update_file=self.update_tar)

	def test_update(self):
		# this test should be self-contained
		self._clear_rule_dir_and_update()

		new_fs = []
		for top, dirs, files in os.walk(self._scanner._yara_rules_dir):
			map(new_fs.append, [os.path.relpath(os.path.join(top, f),self._scanner._yara_rules_dir) for f in files])
		map(self.assertTrue, [f in new_fs for f in self.expected_yara_files_in_update])

	def tearDown(self):
		self.scanner._clear_rule_dir()
		super(TestYaraAV, self).tearDown()
