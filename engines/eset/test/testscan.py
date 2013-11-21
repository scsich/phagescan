
import unittest
from engines.eset.scanner import eset_engine
from engines.generic.test.common import AVEngineTemplate
from nose.tools import ok_


class TestESETAV(AVEngineTemplate, unittest.TestCase):
	scan_class = eset_engine
	infected_string = 'Eicar test file'

	def setUp(self):
		AVEngineTemplate.setUp(self)

	def test_update(self):
		"""
		Run test of A/V definition update functionality.

		This test requires root privs (sudo).
		"""

		# version returns dict, test needs 'definitions' element.
		# definitions is string like: 15481
		# initial ver on A/V defs
		init_ver = self.scanner.version['definitions'].split()[0]
		#print init_ver

		# run update_definitions()
		self.scanner.update_definitions()
		# final date on A/V defs
		final_ver = self.scanner.version['definitions'].split()[0]
		#print final_ver

		# If the defs were updated, final_ver is > init_ver.
		# In the case where they were already updated, then final_ver == init_ver.
		ok_(final_ver >= init_ver, msg="Test A/V def update - version")

