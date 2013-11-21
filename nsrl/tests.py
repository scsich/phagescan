"""

Run "manage.py test nsrl".

"""

from django.test import TestCase
import random
from nsrl.models import NSRLBloomQuery, MD5_KEY_CSV
import os
from nsrl.util import get_all_nsrl_files, read_csv_lines
import tempfile

NSRL_TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test/file')


class SimpleCSVReadTest(TestCase):
	N_ENTRIES_TO_TEST = 100
	# def test_file_process(self):
	# 	# only do a partial of a single file
	# 	nsrl_files = get_all_nsrl_files()
	# 	nsrl_file_rand_to_test = random.choice(nsrl_files)
	# 	n_test_records = 1000
	# 	NSRLFile.objects._process_nsrl_file(nsrl_file_rand_to_test, limit_lines= n_test_records, chunk_size=100)
	# 	self.assertEqual(NSRLFile.objects.count(), n_test_records-1)


	NOT_IN_NSRL = ['f6b44479c464495f0b2f13006de8e872', 'a66c0608be367cab53f1adab9171af66',
				   '862793fa90edaaac87a646dc2f973584']

	def _test_random_entries(self, bq):
		random_file_to_check_with = random.choice(get_all_nsrl_files(iso_base_dir=NSRL_TEST_DATA_DIR))
		test_csv_reader = list(read_csv_lines(random_file_to_check_with))
		sample_lines = random.sample(test_csv_reader, self.N_ENTRIES_TO_TEST)
		for sample_line in sample_lines:
			self.assertTrue(bq.md5_exists(sample_line[MD5_KEY_CSV]),
							"Didn't find MD5 in bloom! {0}".format(sample_lines.index(sample_line)))

	def test_file_process_bloom(self):
		bq = NSRLBloomQuery()
		bq.save_file = tempfile.mktemp()
		bq.nsrl_dir = NSRL_TEST_DATA_DIR
		bq.generate_new_bloom()
		# then do some queries
		self._test_random_entries(bq)
		bq.save_bloom()
		print "File size {0}".format(os.path.getsize(bq.save_file))

	def test_nsrl_saved(self):
		bq = NSRLBloomQuery()

		self._test_random_entries(bq)
		for has in self.NOT_IN_NSRL:
			self.assertFalse(bq.md5_exists(has),
			                 "Hash in NSRL bloom when its not supposed to be {0}".format(self.NOT_IN_NSRL.index(has)))

