
from datetime import datetime
from os import write, close, path
import math
import tempfile
from engines.generic.abstract import AbstractMDEngine, L32_PLATFORM
from engines.generic.exception import UnsupportedFileTypeForScanner


class peid_engine(AbstractMDEngine):
	def __init__(self, engine_path=None):
		super(peid_engine, self).__init__()
		self._engine_path = engine_path
		self._name = 'PEID'
		self._platform = L32_PLATFORM

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		"""
		# pefile.py 1.2.10-123
		# peid.py 0.01
		version = dict()
		version["engine"] = "1.2.10-123"
		return version

	def is_installed(self):
		try:
			import pefile
			import peutils
			return True
		except ImportError:
			return False

	def _build_attributes(self, scan_result):
		import pefile
		# scan_result = pefile.PE('')
		pe_attributes = {
		'optional_header': hex(scan_result.OPTIONAL_HEADER.ImageBase),
		'address_of_entry_point': hex(scan_result.OPTIONAL_HEADER.AddressOfEntryPoint),
		'required_cpu_type': pefile.MACHINE_TYPE[scan_result.FILE_HEADER.Machine],
		'dll': scan_result.is_dll(),
	    'exe': scan_result.is_exe(),
		'driver': scan_result.is_driver(),
		'checksum': scan_result.generate_checksum(),
		'verify_checksum': scan_result.verify_checksum(),
		'subsystem': pefile.SUBSYSTEM_TYPE[scan_result.OPTIONAL_HEADER.Subsystem],
		'compile_time': datetime.fromtimestamp(scan_result.FILE_HEADER.TimeDateStamp),
		'number_of_rva_and_sizes': scan_result.OPTIONAL_HEADER.NumberOfRvaAndSizes
		}
		return pe_attributes

	def _build_analysis(self, scan_result):
		# scan_result = pefile.PE('')
		pe_sections = []
		for section in scan_result.sections:
			pe_sections.append((
			section.Name, hex(section.VirtualAddress), hex(section.Misc_VirtualSize), section.SizeOfRawData,
			self._calculate_entropy(section.get_data())))
		pe_analysis = {
		'number_of_sections': scan_result.FILE_HEADER.NumberOfSections,
		'section_details': pe_sections # "Section Name, VirtualAddress, VirtualSize, SizeofRawData, Entropy"
		}
		return pe_analysis

	## Load PEID userdb.txt database and scan file
	def _build_peid_matches(self, scan_result):
		import peutils
		pe_matches = dict()
		UserDB_FILE_DIR_PATH = path.join(path.dirname(__file__), 'file', 'UserDB.TXT')
		signatures = peutils.SignatureDatabase(UserDB_FILE_DIR_PATH)

		packer = []
		matches = signatures.match_all(scan_result, ep_only=True)
		if matches:
			map(packer.append, [s[0] for s in matches])
		pe_matches["peid_signature_match"] = packer
		pe_matches["is_probably_packed"] = peutils.is_probably_packed(scan_result)
		pe_matches["is_suspicious"] = peutils.is_suspicious(scan_result)
		pe_matches["is_valid"] = peutils.is_valid(scan_result)
		return pe_matches

	def _build_import_address_table(self, scan_result):
		# scan_result = pefile.PE('')
		pe_import_address_table = {}
		dll_dict = {}
		for entry in scan_result.DIRECTORY_ENTRY_IMPORT:
			import_list = list()
			for imp in entry.imports:
				import_list.append(imp.name)
			if entry.dll in dll_dict:
				dll_dict[entry.dll] += import_list
			else:
				dll_dict[entry.dll] = import_list

		pe_import_address_table["imported_dlls"] = dll_dict

		return pe_import_address_table

	# Entropy calculation from Ero Carrera's blog ###############
	def _calculate_entropy(self, data):
		if not data:
			return 0
		entropy = 0
		for x in range(256):
			p_x = float(data.count(chr(x))) / len(data)
			if p_x > 0:
				entropy += - p_x * math.log(p_x, 2)
		return entropy

	def _scan(self, file_object):
		import pefile
		(fpSample, samplePath) = tempfile.mkstemp()
		write(fpSample, file_object.all_content)
		close(fpSample)
		self.mark_path_for_removal(samplePath)
		try:
			pe = pefile.PE(samplePath)
			return pe
		except pefile.PEFormatError:
			raise UnsupportedFileTypeForScanner()

	def _parse_scan_result(self, scan_result):
		files, images, metadata = [], [], dict()
		metadata.update(self.version)
		if scan_result is None:
			return files, images, metadata

		pe_attributes = self._build_attributes(scan_result)
		pe_analysis = self._build_analysis(scan_result)
		pe_matches = self._build_peid_matches(scan_result)
		pe_import_address_table = self._build_import_address_table(scan_result)
		metadata.update(pe_attributes)
		metadata.update(pe_analysis)
		metadata.update(pe_matches)
		metadata.update(pe_import_address_table)
		return files, images, metadata
