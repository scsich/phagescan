
from engines.generic.abstract import AbstractEvilnessEngine, L32_PLATFORM
from engines.generic.exception import ScannerUpdateError
from os import write, close
from subprocess import check_output, CalledProcessError, STDOUT
import tempfile


class avira_engine(AbstractEvilnessEngine):
	# this flag indicates whether we require a file from the master
	_requires_update_file_from_master = False

	def __init__(self, engine_path='/usr/lib/AntiVir/guard/avscan', engine_flags='--batch --alert-action=ignore -v',
				 update_engine='/usr/lib/AntiVir/guard/avupdate-guard', update_engine_flags='--product=Scanner'):
		super(avira_engine, self).__init__()
		self._engine_path = engine_path
		self._engine_flags = engine_flags
		self._update_engine = update_engine
		self._update_engine_flags = update_engine_flags
		self._name = 'Avira'
		self._platform = L32_PLATFORM

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		'definitions': virus definitions file version
		"""

		#$ sudo /usr/lib/AntiVir/guard/avscan --version -v
		#product kind: Avira AntiVir Server (ondemand scanner)
		#product version: 3.1.3.5
		#VDF version: 7.11.55.60
		#VDF date: 2012-12-31
		#AVE version: 8.2.10.224
		#operating system: Linux 3.2.0-33-generic x86_64
		#binary target: linux_glibc22
		#The program is running in fully functional mode.

		# if not self.is_installed():
		# 	raise ScannerNotInstalled

		try:
			raw_version = check_output([self._engine_path, "--version", "-v"])
		except CalledProcessError, e:
			raw_version = e.output

		raw_split = raw_version.split("\n")

		version = dict()
		#Required returns:
		version["definitions"]  = raw_split[2].split(": ")[1]
		version["engine"]       = raw_split[4].split(": ")[1]

		#extra version info:
		version["definitionsDate"]  = raw_split[3].split(": ")[1]
		version["productVersion"]   = raw_split[1].split(": ")[1]
		version["scannerOS"]        = raw_split[5].split(": ")[1]
		version["productName"]      = raw_split[0].split(": ")[1]

		return version

	def is_engine_licensed(self):
		"""
		Determine if it is a valid license.

		Assume that the caller has already checked self.engine_path_exists()
		and self.is_engine_path_executable()

		$ avlinfo
		==============================
		Key file:         /usr/lib/AntiVir/guard/avira.key

		Product : AntiVir Command Line Scanner (Unix)
		Serial #: 2224700406-ACMLM-0000010
		Expires : 10.1.2014
		User    : Narf Industries LLC

		Product : Avira Security Management Center
		Serial #: 2224700406-ASMCM-0000013
		Expires : 10.1.2014
		User    : Narf Industries LLC

		Product : AntiVir for DOS
		Serial #: 2224700406-ARGHM-0000010
		Expires : 10.1.2014
		User    : Narf Industries LLC

		Product : UNKNOWN
		Serial #: 2224700406-MACPM-0000010
		Expires : 10.1.2014
		User    : Narf Industries LLC

		Product : Avira AntiVir Server (Unix)
		Serial #: 2224700406-ASRTM-0000010
		Expires : 10.1.2014
		User    : Narf Industries LLC

		Product : Avira AntiVir Server (Windows) 2003/2000
		Serial #: 2224700406-OEJIM-0000010
		Expires : 10.1.2014
		User    : Narf Industries LLC

		OR

		$ avlinfo
		No key files found

		"""

		try:
			raw_license = check_output(["avlinfo"])
		except CalledProcessError, e:
			raw_license = e.output

		raw_split = raw_license.splitlines()

		if raw_split == "No key files found":
			return False
		else:
			# parse output into dict
			avira_license = dict()
			for idx in range(len(raw_split)):
				line = raw_split[idx]
				# skip decorative lines
				if line.startswith("==") or line == '':
					continue

				left, right = line.split(":")
				left = left.strip()
				right = right.strip()
				if left == "Key file":
					avira_license["key_file"] = right.strip()
				if left == "Product" and right == "AntiVir Command Line Scanner (Unix)":
					avira_license["product"] = right
					avira_license["serial"]  = raw_split[idx+1].split(":")[1].strip()
					avira_license["expires"] = raw_split[idx+2].split(":")[1].strip()
					avira_license["user"]    = raw_split[idx+3].split(":")[1].strip()
					# compare expiration
					from datetime import datetime
					expires = datetime.strptime(avira_license["expires"], '%d.%m.%Y')
					now = datetime.today()
					if expires >= now:
						return True
					else:
						return False

			return False

	def update_definitions(self):
		"""
		Run $ sudo /usr/bin/avastvpsupdate.sh to update the definitions.
		It has to be run with root privs (sudo).

		Example output:
		$ sudo /usr/lib/AntiVir/guard/avupdate-guard
		[sudo] password for avuser:
		Updating, please wait...
		Updated files:
		<snip lots of file names>
		Update finished successfully

		OR - if already update
		Updating, please wait...
		Nothing to update
		"""
		command = ['sudo', self._update_engine]
		for flag in self._update_engine_flags.split():
			command.append(flag)

		try:
			raw_update_output = check_output(command, stderr=STDOUT)
			retcode = 0
		except CalledProcessError, e:
			raw_update_output = e.output
			retcode = e.returncode

		if retcode == 0:
			return
		else:
			raise ScannerUpdateError("Avira definition update failed. {0}".format(raw_update_output))

	def _scan(self, file_object):

		(fpSample, samplePath) = tempfile.mkstemp()
		write(fpSample, file_object.all_content)
		close(fpSample)
		self.mark_path_for_removal(samplePath)

		command = [self._engine_path]
		for flag in self._engine_flags.split():
			command.append(flag)
		command.append(samplePath)

		try:
			return "0\n{0}".format(check_output(command))
		except CalledProcessError as e:
			return "{0}\n{1}".format(e.returncode, e.output)

	def _parse_scan_result(self, scan_result):

		"""
		#Clean file sample output:
		#	0
		#	Avira AntiVir Server (ondemand scanner)
		#	Copyright (C) 2010 by Avira GmbH.
		#	All rights reserved.
		#
		#	SAVAPI-Version: 3.1.1.8, AVE-Version: 8.2.10.224
		#	VDF-Version: 7.11.55.60 created 20121231
		#
		#	AntiVir license: 2224549342
		#
		#	Info: automatically excluding /sys/ from scan (special fs)
		#	Info: automatically excluding /proc/ from scan (special fs)
		#	Info: automatically excluding /home/quarantine/ from scan (quarantine)
		#	scan progress: directory "/home/scanuser/Documents/phage/"
		#
		#	------ scan results ------
		#	   directories: 1
		#    scanned files: 6
		#          skipped: 28
		#           alerts: 0
		#       suspicious: 0
		#        scan time: 00:00:01
		#--------------------------


		#Infected File sample output:
		#1
		#Avira AntiVir Server (ondemand scanner)
		#Copyright (C) 2010 by Avira GmbH.
		#All rights reserved.
		#
		#SAVAPI-Version: 3.1.1.8, AVE-Version: 8.2.10.224
		#VDF-Version: 7.11.55.60 created 20121231
		#
		#AntiVir license: 2224549342
		#
		#Info: automatically excluding /sys/ from scan (special fs)
		#Info: automatically excluding /proc/ from scan (special fs)
		#Info: automatically excluding /home/quarantine/ from scan (quarantine)
		#
		#  file: /home/ender/EICAR
		#	last modified on  date: 2012-10-17  time: 22:54:44,  size: 69 bytes
		#	ALERT: Eicar-Test-Signature ; virus ; Contains code of the Eicar-Test-Signature virus
		#	ALERT-URL: http://www.avira.com/en/threats?q=Eicar%2DTest%2DSignature
		#  no action taken
		#
		#------ scan results ------
		#   directories: 0
		# scanned files: 1
		#		alerts: 1
		#	suspicious: 0
		#	  repaired: 0
		#	   deleted: 0
		#	   renamed: 0
		#		 moved: 0
		#	 scan time: 00:00:01
		#--------------------------
		#

		list of return codes:
		   0: Normal program termination, nothing found, no error
		   1: Found concerning file
		   3: Suspicious file found
		   4: Warnings were issued
		 255: Internal error
		 254: Configuration error (invalid parameter in command-line
			  or configuration file)
		 253: Error while preparing on-demand scan
		 252: The avguard daemon is not running
		 251: The avguard daemon is not accessible
		 250: Cannot initialize scan process
		 249: Scan process not completed
		 248: No valid license found
		 211: Program aborted, because the self check failed

		"""

		infected, infected_string, metadata = False, '', dict()
		metadata.update(self.version)

		retval = int(scan_result.split("\n")[0])
		# TODO: clean up the parsing of return values and actions for them (raise exceptions)
		# normal return, no error, nothing found
		#print "retval:{0}".format(retval)
		if retval == 0:
			return infected, infected_string, metadata
		# normal return, found concerning/suspicious file
		elif retval in [1, 3, 4]:
			infected = True
			tempMeta = scan_result.split("  ")[8]
			infected_string = tempMeta.split(" ; ")[0].split(": ")[1]
			metadata["category"] = tempMeta.split(" ; ")[1]
			metadata["description"] = tempMeta.split(" ; ")[2]
			return infected, infected_string, metadata
		# any errors
		else:
			#TODO: This means something unexpected happened... Whats the proper return?
			return infected, infected_string, metadata
