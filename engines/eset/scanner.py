
from engines.generic.abstract import AbstractEvilnessEngine, L32_PLATFORM
from engines.generic.exception import ScannerUpdateError, ScannerNotInstalled
from os import write, close
from subprocess import check_output, CalledProcessError, Popen, PIPE
import tempfile


class eset_engine(AbstractEvilnessEngine):
	# this flag indicates whether we require a file from the master
	_requires_update_file_from_master = False

	def __init__(self, engine_path='/opt/eset/esets/sbin/esets_scan',
				 engine_flags='--clean-mode=none --no-quarantine',
				 update_engine = "/opt/eset/esets/sbin/esets_update"):
		super(eset_engine, self).__init__()
		self._engine_path = engine_path
		self._engine_flags = engine_flags
		self._update_engine = update_engine
		self._name = 'ESET'
		self._platform = L32_PLATFORM

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		'definitions': virus definitions file version
		"""

		#/opt/eset/esets/sbin/esets_scan --clean-mode=none --no-quarantine /opt/eset/esets/sbin/esets_scan | grep version
		#ESET Command-line scanner, version 4.0.8, (C) 1992-2010 ESET, spol. s r.o.
		#Module loader, version 1040 (20120313), build 1048
		#Module perseus, version 1371 (20121115), build 1494
		#Module scanner, version 7708 (20121119), build 12536
		#Module archiver, version 1156 (20121029), build 1122
		#Module advheur, version 1136 (20121017), build 1101
		#Module cleaner, version 1058 (20121005), build 1066

		if not self.is_installed():
			raise ScannerNotInstalled

		version = dict()

		# To do a pipe w/o shell=True, have to do 2 processes and pipe them together manually.
		eset_command = [self._engine_path] + self._engine_flags.split() + [self._update_engine]
		eset_run = Popen(eset_command, stdout=PIPE)
		grep_command = ["grep", "version"]
		grep_run = Popen(grep_command, stdin=eset_run.stdout, stdout=PIPE)
		eset_run.stdout.close()

		raw_version = grep_run.communicate()[0]
		raw_split = raw_version.split("\n")
		version["engine"] 		= raw_split[0].split(",")[1].split(" ")[2]
		version["loader"] 		= raw_split[1].split("version ")[1]
		version["perseus"] 		= raw_split[2].split("version ")[1]
		version["definitions"] 	= raw_split[3].split("version ")[1]
		version["archiver"] 	= raw_split[4].split("version ")[1]
		version["heuristics"] 	= raw_split[5].split("version ")[1]
		version["cleaner"] 		= raw_split[6].split("version ")[1]

		return version

	def update_definitions(self):
		"""
		Run $ sudo /opt/eset/esets/sbin/esets_update to update the virus definitions.
		It has to be run with root privs (sudo).

		Expected outputs:
		For update not necessary:
		$ sudo /opt/eset/esets/sbin/esets_update
		Update is not necessary - the installed virus signature database is current.
		Installed virus signature database version 8665 (20130808)

		For update needed/performed:
		$ sudo /opt/eset/esets/sbin/esets_update
		Virus signature database has been updated successfully.
		Installed virus signature database version 8681 (20130812)
		"""
		raw_update_output = check_output(["sudo", self._update_engine])
		if raw_update_output:
			raw_split = raw_update_output.split("\n")
			if raw_split and (raw_split[0].startswith("Update is not necessary") or
							  raw_split[0].endswith("updated successfully.")):
				return
			else:
				raise ScannerUpdateError("Eset definition update failed. Unknown failure.")
		else:
			raise ScannerUpdateError("Eset definition update failed. No output returned from updater.")

	def _scan(self, file_object):

		(fpSample, samplePath) = tempfile.mkstemp()
		write(fpSample, file_object.all_content)
		close(fpSample)
		self.mark_path_for_removal(samplePath)

		scan_command = [self._engine_path] + self._engine_flags.split() + [samplePath]
		try:
			return "0\n{0}".format(check_output(scan_command))
		except CalledProcessError as e:
			return "{0}\n{1}".format(e.returncode, e.output)

	def _parse_scan_result(self, scan_result):

		infected, infected_string, metadata = False, '', dict()
		metadata.update(self.version)

		scan_result = scan_result.split("\n\n")
		retval = int(scan_result[0])
		if retval == 0:
			return infected, infected_string, metadata
		elif retval == 50:
			infected = True
			infected_string = scan_result[3].split(", ")[1][8:-1]
			return infected, infected_string, metadata
		else:
			#TODO: This means something bad happened... Whats the proper return?
			return infected, infected_string, metadata
