
from engines.generic.abstract import AbstractMDEngine, L32_PLATFORM
from subprocess import check_output
from os import write, close, path
import tempfile


class pdfid_engine(AbstractMDEngine):

	def __init__(self, engine_path=path.join(path.dirname(path.abspath(__file__)), 'file', 'pdfid.py')):
		super(pdfid_engine, self).__init__()
		self._engine_path = engine_path
		self._name = 'PDFID'
		self._platform = L32_PLATFORM

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		"""
		# $ python pdfid.py --version
		# pdfid.py 0.0.12
		return {'engine': check_output(['python', self._engine_path, '--version']).split()[1]}

	def is_installed(self):
		"""
		This is always installed in file/pdfid.py.

		"""
		return True

	def _scan(self, file_object):

		(fpSample, samplePath) = tempfile.mkstemp()
		write(fpSample, file_object.all_content)
		close(fpSample)
		self.mark_path_for_removal(samplePath)

		return check_output(['python', self._engine_path, samplePath])

	def _parse_scan_result(self, scan_result):

		files, images, metadata = [], [], dict()
		metadata.update(self.version)

		# PDFiD produces no files nor images, so these return items do not apply

		# NOTE: we are no longer concerned with detecting whether a file is "supported" or not, because we assume that
		# this engine will not be called if the MIME-type of the file does not match the _supported_file_types filter.

		metadata['pdfid_rawresult'] = scan_result
		return files, images, metadata
