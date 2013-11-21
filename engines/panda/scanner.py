
import sys
from subprocess import check_output, CalledProcessError, STDOUT
from os import write, close, remove, path
import tempfile, urllib2
import ConfigParser
from zipfile import ZipFile
from engines.generic.abstract import AbstractEvilnessEngine, W32_PLATFORM


class panda_engine(AbstractEvilnessEngine):

	def __init__(self, engine_path='c:\pavcl\Pavcl.exe', engine_flags='-aex -nos -nor -nob'):
		super(panda_engine, self).__init__()
		self._engine_path = engine_path
		self._engine_flags = engine_flags
		self._name = 'Panda'
		self._platform = W32_PLATFORM

	@classmethod
	def os_compatibility(cls):
		return sys.platform == 'win32'

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		"""
		# NOTE: You MUST include a file name after the -info flag!
		# $ pavcl.exe -info <filename>
		# Product version: 9.05.01.0002

		command = [self._engine_path, "-info", self._engine_path]

		try:
			vers = check_output(command, stderr=STDOUT)
		except CalledProcessError, e:
			vers = e.output.splitlines()
		except IOError as e:
			vers = ''

		engineVers	= vers[0].split(': ')[1]
		defsVers	= vers[2].split(': ')[1]
		return {'engine': engineVers, 'definitions': defsVers}

	def update_definitions(self):
		"""
		Panda's pavcl utility has no built-in method to download updates.

		Therefore, we will pull updates manually and extract them to the production directory.

		Downloading the update file pav.zip will require a username and password.
		"""
		self._config_file = path.join(path.dirname(__file__), 'panda.conf')
		update_section_name = 'Update'
		config_options = ['username', 'password', 'install_dir', 'sig_file', 'update_url']

		config = ConfigParser.SafeConfigParser()
		config.read(self._config_file)

		if not config.has_section(update_section_name):
			raise Exception("Error: Config file '{0}' is missing section '[{1}]'".format(
				self._config_file, update_section_name))
		for option in config_options:
			if not config.has_option(update_section_name, option):
				raise Exception("Error: Config file '{0}' is missing option '{1}' in section '[{2}]'".format(
					self._config_file, option, update_section_name))

		update_user = config.get(update_section_name, 'username')
		update_pass = config.get(update_section_name, 'password')
		sig_file = config.get(update_section_name, 'sig_file')
		install_dir = config.get(update_section_name, 'install_dir')
		update_url = config.get(update_section_name, 'update_url')

		# create password manager
		pw_mgr = urllib2.HTTPPasswordMgr()
		pw_mgr.add_password('Panda Antivirus', update_url, update_user, update_pass)

		# create handler that uses HTTP Basic Auth
		url_handler = urllib2.HTTPBasicAuthHandler(pw_mgr)

		# create opener to use url_handler
		url_opener = urllib2.build_opener(url_handler)

		# make this the default opener for all urlopen calls
		urllib2.install_opener(url_opener)

		# write sig_file to a tempfile (rather than keeping it in memory)
		(fpDefs, pathDefs) = tempfile.mkstemp()
		u = urllib2.urlopen(update_url)
		write(fpDefs, u.read())
		close(fpDefs)

		# extract new sig_file to install_dir
		with ZipFile(pathDefs, 'r') as myzip:
			myzip.extract(sig_file, install_dir)

		# rm the temp zip file
		remove(pathDefs)

	def _scan(self, file_object):

		(fpSample, samplePath) = tempfile.mkstemp()
		write(fpSample, file_object.all_content)
		close(fpSample)
		self.mark_path_for_removal(samplePath)

		command = [self._engine_path]
		map(lambda x: command.append(x), self._engine_flags.split())
		command.append(samplePath)

		try:
			scan_result = check_output(command, stderr=STDOUT)
		except CalledProcessError as e:
			scan_result = e.output

		return scan_result

	def _parse_scan_result(self, scan_result):
		"""
		This engine marks files as 'infected' or 'suspicious' or neither
		Number of files infected ...........: 1
		Number of suspicious files .........: 0
		We will consider the file infected if 'infected' = 1
		We will ignore suspicious for the infected indicator, but put it in the metadata
		"""
		infected, infected_string, metadata = False, '', dict()
		metadata.update(self.version)

		infected = scan_result.split('\nPa')[1].split('infected')[1].split()[1] != "0"

		if(infected):
			for string in scan_result.splitlines():
				if string.find(':') != -1:
					tokens = []
					if string.startswith('c:\\'):
						tokens = ['Temp file', string]
					elif string.startswith('Time'):
						tokens = string.split('.: ')
					else:
						tokens = string.split(':')
					if len(tokens) == 2:
						l = tokens[0].split('.')[0].strip()
						r = tokens[1].strip()
						metadata[l] = r
			infected_string = metadata["Found virus"]

		return infected, infected_string, metadata