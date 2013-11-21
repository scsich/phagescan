
from os import path
from engines.generic.exception import ScannerMustSpecifyInfectionName
from scanworker.file import PickleableFileSample


class UnrecognizedFileTypeInMetadataResult(Exception):
	pass


class FilePathMustBeAbsolute(Exception):
	pass


class GenericEvilnessResult(object):
	def __init__(self, hex_digest, infected, infected_string='', metadata=None):
		self.digest = hex_digest
		# todo check this digest is right length etc
		self.infected = infected
		self.infected_string = infected_string
		# todo is it a good idea to make the md just a dict or should it be a full-fledged object?
		self.metadata = metadata if metadata else dict()
		if infected and self.infected_string is '':
			raise ScannerMustSpecifyInfectionName
		# todo put into read only properties


class GenericMDResult(object):
	def __init__(self, hex_digest, files, images, metadata):
		# todo integrate with generic scanresult above
		self.metadata = metadata if metadata else dict()
		self.digest = hex_digest

		# verify pickleable-ness
		self.files = map(self._ensure_file_is_pickleable, set(files))
		self.images = map(self._ensure_file_is_pickleable, set(images))

		# this is to allow MD results to play nice if their engine is also an evilness engine
		self.infected = self.metadata['infected'] if 'infected' in self.metadata else None
		self.infected_string = self.metadata['infected_string'] if 'infected_string' in self.metadata else None

	def _ensure_file_is_pickleable(self, file_sample):
		pickleable_file = None
		if isinstance(file_sample, str):
			# treat all strings in this list as a path
			if not path.isabs(file_sample):
				raise FilePathMustBeAbsolute()
			pickleable_file = PickleableFileSample.path_factory(file_sample)
		elif isinstance(file_sample, PickleableFileSample):
			pickleable_file = file_sample

		if not pickleable_file:
			raise UnrecognizedFileTypeInMetadataResult

		return pickleable_file
