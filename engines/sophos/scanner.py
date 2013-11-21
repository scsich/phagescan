
from os import write, close
from subprocess import check_output, CalledProcessError
import tempfile, urllib2, os
from engines.generic.abstract import L32_PLATFORM, AbstractEvilnessEngine


class sophos_engine(AbstractEvilnessEngine):
	# this flag indicates whether we require a file from the master
	_requires_update_file_from_master = False

	def __init__(self, engine_path='/usr/local/bin/sweep'):
		super(sophos_engine, self).__init__()
		self._engine_path = engine_path
		self._name = 'Sophos'
		self._platform = L32_PLATFORM

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		'definitions': virus definitions file version
		"""

		# Best way to get version information is to run "sweep -v" and get the lines containing 'version'.
		# Output will look like the following:
		#Product version           : 4.81.0
		# <snip>
		#Engine version            : 3.35.1
		# <snip>
		#Virus data version        : 4.81
		# <snip>
		#User interface version    : 2.07.354
		# <snip>
		version = dict()
		tmp = check_output([self._engine_path, '-v'])
		tmp_vers = [line for line in tmp.splitlines() if line.find('version') != -1]
		version["engine"]		= tmp_vers[0].split(": ")[1]
		version["definitions"]	= tmp_vers[2].split(": ")[1]
		return version

	def update_definitions(self):
		"""
		Sophos' sweep utility has no built-in method to download updates.

		Therefore, we will pull updates manually and extract them to the production directory.
		"""

		# build update URL
		self._update_url = 'http://downloads.sophos.com/downloads/ide/{0}_ides.zip'.format(self.version["definitions"].strip().replace('.', ''))

		# get the update package, write to a file (rather than keep in memory)
		(fpDefs, pathDefs) = tempfile.mkstemp()
		u = urllib2.urlopen(self._update_url)
		os.write(fpDefs, u.read())
		os.close(fpDefs)

		# extract the update package
		check_output(['sudo', '/usr/bin/unzip', '-o', pathDefs, '-d', '/usr/local/sav'])

		# rm the update package
		os.remove(pathDefs)

	def _scan(self, file_object):

		(fpSample, samplePath) = tempfile.mkstemp()
		write(fpSample, file_object.all_content)
		close(fpSample)
		self.mark_path_for_removal(samplePath)

		try:
			return check_output([self._engine_path, "-ss", samplePath])
		except CalledProcessError as e:
			return e.output

	def _parse_scan_result(self, scan_result):

		infected, infected_string, metadata = False, '', dict()
		metadata.update(self.version)

		if scan_result == infected_string: return infected, infected_string, metadata

		infected = True
		infected_string = scan_result.split(" ")[2][1:-1]
		return infected, infected_string, metadata
