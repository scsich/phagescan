
from engines.generic.abstract import AbstractEvilnessEngine, L32_PLATFORM
from engines.generic.exception import ScannerUpdateError
from subprocess import  check_output, CalledProcessError, STDOUT
from os import  write, close
import tempfile
from time import sleep


class symantec_engine(AbstractEvilnessEngine):
	# this flag indicates whether we require a file from the master
	_requires_update_file_from_master = False

	def __init__(self,
				 engine_path='/opt/SYMCScan/ssecls/ssecls',
				 engine_flags='-mode scan -onerror leave -details -verbose',
				 update_engine='/root/av_sig_updater.sh',
				 update_engine_flags='symantec',
				 init_path='/etc/init.d/symcscan'):
		super(symantec_engine, self).__init__()
		self._engine_path = engine_path
		self._engine_flags = engine_flags
		self._init_path = init_path
		self._update_engine = update_engine
		self._update_engine_flags = update_engine_flags
		self._name = 'Symantec'
		self._platform = L32_PLATFORM

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		'definitions': virus definitions file version
		'product': branded version
		"""
		version = {}
		# we are going to scan a known clean file that is world-readable and grab the defs version string from the output.
		command = ['sudo', self._engine_path] + self._engine_flags.split() + ['/etc/resolv.conf']

		try:
			raw_version1 = check_output(command, stderr=STDOUT)
		except CalledProcessError, e:
			raw_version1  = e.output
			if raw_version1.startswith("Error: unable to connect"):
				try:
					# "first attempt failed..."
					sleep(3)
					# "trying again..."
					raw_version1 = check_output(command, stderr=STDOUT)
				except CalledProcessError, er:
					raw_version1 = er.output

		version['definitions'] = raw_version1.split(" = ")[1].split("\n ")[0]
		try:
			raw_version2 = check_output(['sudo', self._init_path, "version"])
		except CalledProcessError, e:
			raw_version2 = e.output
		version['product'], version['engine'] = raw_version2.strip().split(" Version: ")
		return version

	def is_update_needed(self):
		"""
		Compare current definitions to the latest available to determine if a defn update is necessary.

		Returns True if latest available update version is newer than the currently installed definitions version.
		else False
		"""
		import urllib2
		url='ftp://ftp.symantec.com/public/english_us_canada/antivirus_definitions/norton_antivirus/'
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		avail_updates=[]
		for line in response.read().splitlines():
			f = line.split()[-1]
			if f.endswith('-unix.sh'):
				avail_updates.append(f)

		#avail_updates: ['20130817-006-unix.sh', '20130818-004-unix.sh', '20130819-001-unix.sh', '20130820-002-unix.sh']
		yr, ver, end = avail_updates[-1].split('-')
		latest_ver = "{0}.{1}".format(yr,ver)
		#version['definitions'] = '20130820.002'
		installed_ver = self.version['definitions']
		# print "latest: {0}, current: {1}".format(latest_ver, installed_ver)
		if latest_ver > installed_ver:
			return True
		else:
			return False

	def update_definitions(self):
		"""
		Update the definitions.
		It has to be run with root privs (sudo).

		This process is move involved because of some bugs in the actual updater scripts.
		(e.g. LiveUpdate doesn't seem to work correctly)

		To do an update, run:
		sudo /root/av_sig_updater.sh symantec

		retcode 0: success
		retcode 1: failure/error

		Note: running this update will take about 15-20 minutes, depending on bandwidth.
		The update file is around 500MB.
		"""

		try:
			raw_update_output = check_output(['sudo', self._update_engine, self._update_engine_flags], stderr=STDOUT)
			retcode = 0
		except CalledProcessError, e:
			raw_update_output = e.output
			retcode = e.returncode

		if retcode == 0:
			# print "raw_update_output: {0}".format(raw_update_output)
			return
		else:
			raise ScannerUpdateError("Symantec definition update failed. {0}".format(raw_update_output))

	def _parse_scan_result(self, scan_result):

		infected, infected_string, metadata = False, '', dict()
		metadata.update(self.version)

		infected = scan_result.split("Infected")[1].split()[1] != "0"

		if infected:
			for string in scan_result.split("\n\n")[0].splitlines():
				tokens=string.split("\t")
				if len(tokens) == 3:
					metadata[tokens[1][:-2]] = tokens[2]

			infected_string = metadata["Virus Name"]

		return infected, infected_string, metadata

	def _scan(self, file_object):

		(fpSample, pathSample) = tempfile.mkstemp()
		write(fpSample, file_object.all_content)
		close(fpSample)
		self.mark_path_for_removal(pathSample)

		command = ['sudo', self._engine_path]
		for flag in self._engine_flags.split():
			command.append(flag)
		command.append(pathSample)
		try:
			scan_result = check_output(command)
		except CalledProcessError as e:
			scan_result = e.output

		return scan_result
