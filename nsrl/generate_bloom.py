
import os
from optparse import OptionParser
from models import NSRLBloomQuery


def main():

	usage = "usage: %prog [options] arg"
	parser = OptionParser()
	parser.add_option("-f", dest="filename")

	options, args = parser.parse_args()
	if len(args) != 1:
		print "Missing NSRL dir args"
		print usage
		exit(1)

	bq = NSRLBloomQuery()
	if not os.path.isdir(args[0]):
		print "Need valid NSRL dir path"
	bq.nsrl_dir = args[0]
	if options.filename:
		bq.save_file = options.filename
	bq.generate_new_bloom()
	bq.save_bloom()
	print "Generated bloom filter file of size {0}".format(os.path.getsize(bq.save_file) / (10 ** 6))

if __name__ == "__main__":
	main()