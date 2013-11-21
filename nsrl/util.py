
import csv
import os

ISO_BASE = os.path.join(os.path.dirname(__file__), 'iso')
# taken from nsrl2sqlite


def get_all_nsrl_files(iso_base_dir = None):
	if iso_base_dir is None:
		iso_base_dir = ISO_BASE
	dir_w = os.walk(iso_base_dir)
	nsrl_files = []
	for dirpath, dirlist, flist in dir_w:

		map(nsrl_files.append, [os.path.join(dirpath, fname) for fname in filter(lambda dir_dirpaths_files: dir_dirpaths_files.endswith('NSRLFile.txt'), flist)])
	return nsrl_files


def read_csv_lines(fname):

	csv_rdr = csv.DictReader(open(fname, 'r'))
	# fixup fieldname for django model integration
	csv_rdr.fieldnames[csv_rdr.fieldnames.index('SHA-1')] = "SHA1"
	return csv_rdr

