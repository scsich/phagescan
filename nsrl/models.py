
import os
from util import read_csv_lines, get_all_nsrl_files
import itertools
import bz2
from pybloom import ScalableBloomFilter, BloomFilter

BLOOM_FILE = os.path.join(os.path.dirname(__file__), 'file', 'nsrl.bloom')
CHUNK_SIZE = 1000
MD5_KEY_CSV = 'MD5'


def grouper(iterable, n, fillvalue=None):
	"""
		Collect data into fixed-length chunks or blocks
	"""
	# grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
	args = [iter(iterable)] * n
	return itertools.izip_longest(fillvalue=fillvalue, *args)


class NSRLCommon(object):
	def _process_nsrl_file(self, nsrl_file, process_func, limit_lines=0, chunk_size=CHUNK_SIZE):

		csv_reader = read_csv_lines(nsrl_file)
		record_count =  0
		for csv_entry_chunk in grouper(csv_reader, chunk_size):

			process_func(csv_entry_chunk)
			record_count += len(csv_entry_chunk)
			if limit_lines and csv_reader.line_num >= limit_lines:
				break
		return record_count


class NSRLBloomQuery(NSRLCommon):
	capacity = 30 * (10 ** 6)
	error_rate = 0.001
	nsrl_dir = None
	save_file = BLOOM_FILE
	estimate_capacity = True

	def _get_fobj_of_savefile(self, mode):
		open_func = bz2.BZ2File if self.save_file.endswith('bz2') else open
		return open_func(self.save_file, mode)

	def _get_bloom_class(self):
		return BloomFilter if self.estimate_capacity else ScalableBloomFilter

	def _get_bloom_class_inst(self, capacity, error):

		return self._get_bloom_class()(capacity, error)

	@property
	def bloom(self):
		if not hasattr(self, '_bloom'):
			with self._get_fobj_of_savefile('r') as f:
				self._bloom = self._get_bloom_class().fromfile(f)
				f.close()

		return self._bloom

	def _filter_csv_chunk(self, csv_chunk):
		return filter(lambda x: x is not None, csv_chunk)

	def _process_csv_chunk(self, csv_chunk):
		b = self.bloom

		for csv_entry in self._filter_csv_chunk(csv_chunk):
			b.add(csv_entry[MD5_KEY_CSV].lower())

	def _estimate_number_of_recs(self):
		s = set()

		def add_csv_to_set(csv_chunk):
			for csv_entry in self._filter_csv_chunk(csv_chunk):
				s.add(csv_entry[MD5_KEY_CSV])

		for nsrl_file in get_all_nsrl_files(iso_base_dir=self.nsrl_dir):
			self._process_nsrl_file(nsrl_file, add_csv_to_set)
		s_count = len(s)
		# this is doing to get large, but at least we'll have a more exact estimate that strips out doubles

		return s_count

	def _est_num_recs_and_set(self):
		print "Estimating capacity of bloom...."
		self.capacity = self._estimate_number_of_recs() + (10 ** 3)
		print "Setting capacity to {0}.".format(self.capacity)

	def generate_new_bloom(self):

		if self.estimate_capacity:
			self._est_num_recs_and_set()

		self._bloom = self._get_bloom_class_inst(self.capacity, self.error_rate)

		for nsrl_file in get_all_nsrl_files(iso_base_dir=self.nsrl_dir):
			self._process_nsrl_file(nsrl_file, self._process_csv_chunk)

	def md5_exists(self, md5):
		return md5.lower() in self.bloom

	def save_bloom(self):
		with self._get_fobj_of_savefile('w+') as f:
			self.bloom.tofile(f)
			f.close()
