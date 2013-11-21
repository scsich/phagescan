
import unittest
from nose.tools import ok_
from engines.clamav.scanner import clamav_engine
from engines.generic.test.common import AVEngineTemplate


class TestClamAV(AVEngineTemplate,unittest.TestCase):
	scan_class = clamav_engine
	infected_string = 'Eicar-Test-Signature'

	def setUp(self):
		AVEngineTemplate.setUp(self)

	def test_update(self):
		"""
		Run test of A/V definition update functionality.

		This test requires root privs (sudo or setuid root).
		"""

		# version returns dict, test needs 'definitions' element.
		# definitions is string like: 15481
		# initial ver on A/V defs
		init_ver = self.scanner.version['definitions']
		#print init_ver

		# run update_definitions()
		self.scanner.update_definitions()
		# final date on A/V defs
		final_ver = self.scanner.version['definitions']
		#print final_ver

		# If the defs were updated, final_ver is > init_ver.
		# In the case where they were already updated, then final_ver == init_ver.
		ok_(final_ver >= init_ver, msg="Test A/V def update - version")

