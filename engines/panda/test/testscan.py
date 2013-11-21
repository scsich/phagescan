
import unittest
from engines.panda.scanner import panda_engine
from engines.generic.test.common import AVEngineTemplate
from nose.tools import ok_


class TestPandaAV(AVEngineTemplate,unittest.TestCase):
	scan_class = panda_engine
	infected_string ='EICAR-AV-TEST-FILE'

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

	def test_ver(self):
		# print "version: {0}".format(self.scanner.version)
		vers = self.scanner.version
		ok_(vers['engine'] != '', msg="Problem with version() function.")


