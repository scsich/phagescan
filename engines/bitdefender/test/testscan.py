
import unittest
from nose.tools import ok_
from engines.bitdefender.scanner import bitdefender_engine
from engines.generic.test.common import AVEngineTemplate


class TestBitDefenderAV(AVEngineTemplate,unittest.TestCase):
	scan_class = bitdefender_engine
	infected_string = 'EICAR-Test-File (not a virus)'

	def setUp(self):
		AVEngineTemplate.setUp(self)

	def test_update(self):
		"""
		Run test of A/V definition update functionality. This test requires root privs (sudo).
		"""

		# version returns dict: {'engine': engineVers, 'definitions': defsVers }

		# initial ver on A/V defs
		init_ver = self.scanner.version['definitions']

		# run update_definitions()
		self.scanner.update_definitions()

		# final date on A/V defs
		final_ver = self.scanner.version['definitions']

		# If the defs were updated, final_ver is > init_ver.
		# In the case where they were already updated, then final_ver == init_ver.

		ok_(final_ver >= init_ver,
		    msg="Test A/V def update - version. final_ver: '{0}', init_ver: '{1}'".format(final_ver, init_ver))
