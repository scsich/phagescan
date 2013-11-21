
from nose.tools import ok_
from time import sleep
import unittest
from engines.symantec.scanner import symantec_engine
from engines.generic.test.common import AVEngineTemplate

# TODO: get Symantec tests running in CI


class TestSymantecAV(AVEngineTemplate,unittest.TestCase):
	scan_class = symantec_engine
	infected_string = 'EICAR Test String'

	def setUp(self):
		if not self.scan_class().engine_path_exists():
			raise unittest.SkipTest()
		AVEngineTemplate.setUp(self)

	def test_update(self):
		"""
		Run test of A/V definition update functionality.

		This test requires root privs (sudo).
		"""

		# version returns dict, test needs 'definitions' element.
		# definitions is string like: 15481
		# initial ver on A/V defs
		#print self.scanner.version
		init_ver = self.scanner.version['definitions']
		#print init_ver

		# run update_definitions()
		self.scanner.update_definitions()
		# final date on A/V defs
		# Update has to restart the engine, so need to give it a moment to get fully up and running.
		sleep(5)
		final_ver = self.scanner.version['definitions']
		#print final_ver

		# If the defs were updated, final_ver is > init_ver.
		# In the case where they were already updated, then final_ver == init_ver.
		ok_(final_ver >= init_ver, msg="Test A/V def update - version failed.")

	def test_is_update_needed(self):
		ok_(self.scanner.is_update_needed() != None, msg="Is_update_needed failed.")








