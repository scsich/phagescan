
from os import path, mkdir, unlink
import shutil
from StringIO import StringIO
import tarfile
import tempfile
from scanworker.file import PickleableFileSample
from engines.generic.abstract import AbstractEvilnessEngine, L32_PLATFORM
from engines.yara.exception import YaraRuleDirectoryNotFound

OTHER_INFECTED_DICT_K = 'other_infected_d'
NON_INFECTED_RULE_MATCH_K = 'other_rule_match'


class yara_engine(AbstractEvilnessEngine):
	# this flag indicates whether we require a file from the master
	_requires_update_file_from_master = True
	_version_file = 'repo.version'

	def make_rules_dir(self, rules_dir):
		if rules_dir is None:
			self._yara_rules_dir = path.join(path.dirname(__file__), 'rules')
			if not path.exists(self._yara_rules_dir):
				mkdir(self._yara_rules_dir)
		else:
			self._yara_rules_dir = rules_dir

	def __init__(self, engine_path=None, rules_dir=None, repo_rules_dir=None):
		super(yara_engine, self).__init__()
		self._engine_path = engine_path
		self._name = 'Yara'
		self._platform = L32_PLATFORM
		self.make_rules_dir(rules_dir)
		if repo_rules_dir is None:
			self._yara_repo_rules_dir = path.join(path.dirname(__file__), 'repo')
		else:
			self._yara_repo_rules_dir = repo_rules_dir
		self._yara_ext = '.yara'
		# this means that anything in the infected folder/namespace will be considered infected
		self._infected_namespace = 'infected'

		self._version_file_full = path.join(self._yara_repo_rules_dir, self._version_file)

	def _clear_dir(self, d, remake=False):
		if path.exists(d):
			assert (path.isdir(d))
			shutil.rmtree(d)
		if remake:
			mkdir(d)

	def _clear_repo_dir(self):
		self._clear_dir(self._yara_repo_rules_dir)

	def _clear_rule_dir(self):
		self._clear_dir(self._yara_rules_dir, remake=True)

	def get_update_file_factory(self):
		def generate_yara_update_file(path=self._yara_repo_rules_dir):
			import vcs

			# don't move these imports! they're not needed on the worker
			from constance import config
			rule_repo = None
			try:
				rule_repo = vcs.get_backend(config.YARA_REPO_TYPE)(path, create=True, src_url=config.YARA_REPO_URL)
			except vcs.RepositoryError:
				# this means its already there ....
				rule_repo = vcs.get_repo(path=path, create=False)
			# ensure that we have the latest copy
			# todo detect when the repo url is changed and blow it away
			rule_repo.run_git_command("pull")
			tmp_path = tempfile.mktemp(suffix='.tar')
			rule_repo.run_git_command("checkout")
			rule_repo.run_git_command("archive master -o {0}".format(tmp_path))
			temp_ver_path = tempfile.mktemp()

			with open(temp_ver_path, 'w') as version_file_obj:

				version_file_obj.write(str(rule_repo.get_changeset().revision))
				version_file_obj.flush()
			with open(temp_ver_path, 'r') as version_file_obj:
				with tarfile.open(tmp_path, 'a') as tf:
					version_info = tf.gettarinfo(name=self._version_file, fileobj=version_file_obj, arcname=self._version_file)
					tf.addfile(version_info, fileobj=version_file_obj)
					tf.close()

			pfs_update = PickleableFileSample.path_factory(tmp_path)

			unlink(tmp_path)
			unlink(temp_ver_path)
			return pfs_update
		return generate_yara_update_file

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		'definitions': virus definitions file version
		"""
		import yara
		# todo insert definitions (git version) version
		return {'engine': yara.__version__, 'definitions': self._get_def_version()}

	def update_definitions(self, update_file):
		# todo make the yara rules dir unlink more safe by checking its parent too
		# todo compile each file and flag update as good/bad remove if file is bad

		self._clear_rule_dir()

		tf = tarfile.TarFile(fileobj=StringIO(update_file.all_content))
		# one swoop extraction which ensures that we don't leave our path

		yara_files_only = filter(lambda mem: mem.name.endswith(self._yara_ext) or
		                                     mem.name.endswith(self._version_file), tf.getmembers())

		tf.extractall(path = self._yara_rules_dir, members=yara_files_only)

	def engine_path_exists(self):
		try:
			import yara
		except:
			return False

		return True

	def _scan_with_yara_sig(self, full_paths, dirname, files):

		full_paths += filter(lambda fpath: fpath.endswith(self._yara_ext), filter(path.isfile, [path.join(dirname, rule_file) for rule_file in files]))

	def _make_namespace_from_path(self, pth):
		return path.relpath(pth, self._yara_rules_dir)

	def _scan(self, file_object):
		import yara

		scan_results = []
		full_yara_sig_paths = []

		if path.exists(self._yara_rules_dir):

			path.walk(self._yara_rules_dir, self._scan_with_yara_sig, full_yara_sig_paths)

			yara_namespace_dict = dict([(self._make_namespace_from_path(rule_path),rule_path) for rule_path in full_yara_sig_paths])
			rules = yara.compile(filepaths = yara_namespace_dict)
			result = None

			try:
				# Attempt to match the file to one or more rules
				result = rules.match(data=file_object.all_content)
				#todo narrow exception and print a bad file
			except:
				pass

			if result:
				scan_results.append(result)

		else:
			raise YaraRuleDirectoryNotFound()

		return scan_results

	def _parse_scan_result(self, scan_results):
		infected, infected_string, metadata = False, '', dict()
		metadata.update(self.version)

		for result in scan_results:
			for name_space, result_list in result.items():

				if self.namespace_is_infected(name_space):
					for match in result_list:
						infected = True
						if infected_string == '':
							infected_string = match['rule']
						# save all the data from the rule match ... assuming it's picklable
						metadata.setdefault(OTHER_INFECTED_DICT_K, list()).append(match)
				else:
					# store the other matches into an informational only dictionary
					[metadata.setdefault(NON_INFECTED_RULE_MATCH_K, list()).append(match) for match in result_list]
		return infected, infected_string, metadata

	def namespace_is_infected(self, name_space):
		return name_space.startswith(self._infected_namespace)

	def _get_def_version(self):
		version = "Unknown"
		try:
			with open(path.join(self._yara_rules_dir, self._version_file), 'r') as ver_file_obj:
				version = ver_file_obj.readline().rstrip()
				ver_file_obj.close()
			return version
		except IOError:
			return version
