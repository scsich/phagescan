
from engines.generic.abstract import AbstractEvilnessEngine, L32_PLATFORM
from engines.generic.exception import ScannerUpdateError
from subprocess import check_output, CalledProcessError
from os import write, close
import tempfile


class bitdefender_engine(AbstractEvilnessEngine):
	# this flag indicates whether we require a file from the master
	_requires_update_file_from_master = False

	def __init__(self, engine_path='/usr/bin/bdscan'):
		super(bitdefender_engine, self).__init__()
		self._engine_path = engine_path
		self._name = 'BitDefender'
		self._platform = L32_PLATFORM

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		'definitions': virus definitions file version
		"""

		# $ bdscan --info
		# BitDefender Antivirus Scanner for Unices v7.90123 Linux-i586
		# Copyright (C) 1996-2009 BitDefender. All rights reserved.
		# Trial key found. 29 days remaining.
		#
		# Loading plugins, please wait
		# Plugins loaded.
		#
		# Engine signatures: 9769166
		# ...
		# Version: 7.49788
		# ...

		_defsString     = "Engine signatures: "
		_engineString   = "Version: "

		engineVers = defsVers = None

		vers = check_output([self._engine_path, '--info'])
		for line in vers.split('\n'):

			# optimize (slightly)
			if engineVers and defsVers: break

			# find definitions version
			idx = line.find(_defsString)
			if idx != -1:
				defsVers = line[len(_defsString) + idx:]

			# find engine version
			idx = line.find(_engineString)
			if idx != -1:
				engineVers = line[idx + len(_engineString):]

		return {'engine': engineVers, 'definitions': defsVers}

	def update_definitions(self):

		# Example output:
		# $ sudo bdscan --update
		# BitDefender Antivirus Scanner for Unices v7.90123 Linux-i586
		# Copyright (C) 1996-2009 BitDefender. All rights reserved.
		# Trial key found. 29 days remaining.
		#
		# emalware.198 . updated
		# emalware.198  updated
		# ... SNIP ...

		try:
			check_output(['sudo', self._engine_path, "--update"])
		except CalledProcessError, e:
			raise ScannerUpdateError(e.output.split('\n'))

	def _scan(self, file_object):

		(fpSample, samplePath) = tempfile.mkstemp()
		write(fpSample, file_object.all_content)
		close(fpSample)
		self.mark_path_for_removal(samplePath)

		try:
			return check_output([self._engine_path, "--action=ignore", samplePath])
		except CalledProcessError as e:
			return e.output

	def is_engine_licensed(self):
		try:
			check_output([self._engine_path])
			return True
		except CalledProcessError:
			# unlicensed copy will return a exit status of 255
			return False

	def _parse_scan_result(self, scan_result):

		# --- EICAR ---
		# BitDefender Antivirus Scanner for Unices v7.90123 Linux-i586
		# Copyright (C) 1996-2009 BitDefender. All rights reserved.
		# Trial key found. 29 days remaining.
		#
		# Infected file action: ignore
		# Suspected file action: ignore
		# /tmp/tmpCCjGu3  infected: EICAR-Test-File (not a virus)
		#
		#
		# Results:
		# Folders: 0
		# Files: 1
		# Packed: 0
		# Archives: 0
		# Infected files: 1
		# Suspect files: 0
		# Warnings: 0
		# Identified viruses: 1
		# I/O errors: 0

		# --- benign ---
		# BitDefender Antivirus Scanner for Unices v7.90123 Linux-i586
		# Copyright (C) 1996-2009 BitDefender. All rights reserved.
		# Trial key found. 29 days remaining.
		#
		# Infected file action: ignore
		# Suspected file action: ignore
		# /tmp/tmp8j0EMU  ok
		#
		#
		# Results:
		# Folders: 0
		# Files: 1
		# Packed: 0
		# Archives: 0
		# Infected files: 0
		# Suspect files: 0
		# Warnings: 0
		# I/O errors: 0

		_infectedString = "infected: "

		infected, infected_string, metadata = False, '', dict()
		metadata.update(self.version)

		for line in scan_result.split('\n'):
			idx = line.find(_infectedString)
			if idx == -1:
				continue

			# found infection
			infected = True
			infected_string = line[idx + len(_infectedString):]
			return infected, infected_string, metadata

		# not infected
		return infected, infected_string, metadata
