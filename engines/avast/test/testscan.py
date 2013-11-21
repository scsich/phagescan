
import unittest
from nose.tools import ok_
from engines.avast.scanner import avast_engine
from engines.generic.test.common import AVEngineTemplate


class TestAvastAV(AVEngineTemplate, unittest.TestCase):
	scan_class = avast_engine
	infected_string = 'EICAR Test-NOT virus!!!'

	def setUp(self):
		AVEngineTemplate.setUp(self)

	def test_update(self):
		"""
		Run test of A/V definition update functionality. This test requires root privs (sudo).
		"""

		# version returns dict: {'engine': engineVers, 'definitions': defsVers }
		# defsVers is string: 130808-1  (YYMMDD-COUNT)
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


class TestAvastParsing(unittest.TestCase):
	scan_class = avast_engine
	fake_sample_path = '/tmp/blah/sample'
	output = 'Archived /tmp/blah/sample/_5_SummaryInformation\t[OK]\nArchived /tmp/blah/sample/Pictures\t[OK]\nArchived /tmp/blah/sample/_5_DocumentSummaryInformation\t[OK]\nArchived /tmp/blah/sample/PowerPoint Document\t[OK]\n/tmp/blah/sample\t[OK]\n'

	def test_dont_fail_on_this_blob(self):
		self.scan_class.version = {}
		sc = self.scan_class()
		# patch out some stuff

		sc.samplePath = self.fake_sample_path
		infected, infected_string, metadata = sc._parse_scan_result(self.output)
		self.assertEqual(infected, False, msg="Infected string was '{0}'".format(infected_string))
		self.assertEqual(infected_string, '')

