
from engines.generic.abstract import AbstractEvilnessEngine, L32_PLATFORM
from engines.generic.exception import ScannerUpdateError
from os import write, close, devnull
from os.path import split
from xml.dom.minidom import parseString
from subprocess import call, check_output, CalledProcessError, STDOUT
import tempfile


class kaspersky_engine(AbstractEvilnessEngine):
	# this flag indicates whether we require a file from the master
	_requires_update_file_from_master = False

	def __init__(self, engine_path='/opt/kaspersky/kes4lwks/bin/kes4lwks-control'):
		super(kaspersky_engine, self).__init__()
		self._engine_path = engine_path
		self._update_engine = self._engine_path
		self._name = 'Kaspersky'
		self._platform = L32_PLATFORM

	@property
	def version(self):
		"""
		Version numbers for scanner components.
		'engine': scanner engine version
		'definitions': virus definitions file version
		"""

		# The --app-info flag gives us output like the following:
		# Name:                Kaspersky Endpoint Security 8 for Linux
		# Version:             8.0.0.35
		# Install date:        2012-10-15 22:09:40
		# License state:       Installed
		# License expire date: 2012-11-15
		version = dict()
		output_appinfo = check_output(["sudo", self._engine_path, '--app-info'])
		appinfo_lines = output_appinfo.splitlines()
		version['product'] = appinfo_lines[0].split(':')[1].strip()
		version['engine'] = appinfo_lines[1].split(':')[1].strip()
		version['install_date'] = appinfo_lines[2].split(':')[1].strip()
		version['license_state'] = appinfo_lines[3].split(':')[1].strip()
		version['license_expiration'] = appinfo_lines[4].split(':')[1].strip()

		# $ sudo /opt/kaspersky/kes4lwks/bin/kes4lwks-control --get-stat Update
		# Current AV databases date:     2013-08-14 15:52:00
		# Last AV databases update date: 2013-08-14 20:16:08
		# Current AV databases state:    UpToDate

		output_defns = check_output(['sudo', self._engine_path, '--get-stat', 'Update'])
		defns_lines = output_defns.splitlines()
		version['definitions'] = appinfo_lines[0].split(':')[1].strip()
		version['last_update'] = appinfo_lines[1].split(':')[1].strip()
		version['defn_state'] = appinfo_lines[2].split(':')[1].strip()

		return version
		#return { 'engine': check_output([self._engine_path , '--app-info']).split("\n")[1].split()[1] }

	def is_engine_licensed(self):
		# Kaspersky provides a handy means to check its licensing status:
		# $ sudo /opt/kaspersky/kes4lwks/bin/kes4lwks-control --query-status
		# License status:
		# Aggregate expiration date:           2012-11-15
		# Days remaining until expiration:     11
		# Functionality:                       Full functionality
		# License status:                      Valid
		# Active license number:               1106-000451-181CAD96
		output = check_output(["sudo", self._engine_path, '--app-info'])

		license_key_info = map(lambda x: str.split(x, ":"),
		                       filter(lambda x: x.startswith('License state:'), output.splitlines()))
		for keyname, license_state in license_key_info:
			state = license_state.lstrip().rstrip()
			if state == "Installed":
				return True
		return False

	def update_definitions(self):
		"""
		Run kes4lwks-control to update the definitions.
		It has to be run with root privs (sudo).


		Commands that operate on AV Defn Update: (Note, Update is task ID 6)
		Get status of AV database
		$ sudo /opt/kaspersky/kes4lwks/bin/kes4lwks-control --get-stat Update
		Current AV databases date:     2013-08-14 15:52:00
		Last AV databases update date: 2013-08-14 20:16:08
		Current AV databases state:    UpToDate
		Current AV databases records:  10956496
		Update attempts:               3
		Successful updates:            2
		Update manual stops:           0
		Updates failed:                0

		Get AV Update Task State
		$ sudo /opt/kaspersky/kes4lwks/bin/kes4lwks-control --get-task-state Update -N
		Name: Update
		Id: 6
		Runtime ID: 1376508084
		Class: Update
		State: Started

		Start AV Update Task
		$ sudo /opt/kaspersky/kes4lwks/bin/kes4lwks-control --start-task Update -N
		The task has been started, runtime ID: 1376508084.

		Get status of AV Update Task
		$ sudo /opt/kaspersky/kes4lwks/bin/kes4lwks-control --progress Update -N
		Task progress...            ########################################### [100%]

		"""
		command = ['sudo', self._update_engine]
		command_start_task = command + ["--start-task", "Update", "-N"]
		command_task_progress = command + ["--progress", "Update", "-N"]

		try:
			callret = call(command_start_task)
		except CalledProcessError, e:
			callret = e.returncode

		try:
			raw_update_output = check_output(command_task_progress, stderr=STDOUT)
			retcode = 0
		except CalledProcessError, e:
			raw_update_output = e.output
			retcode = e.returncode

		if retcode == 0:
			return
		else:
			raise ScannerUpdateError("Kaspersky definition update failed. {0}".format(raw_update_output))

	def _scan(self, file_object):

		# The Kaspersky control utility is loud
		fhNULL = open(devnull, "w")

		# create temporary sample file
		(fpSample, samplePath) = tempfile.mkstemp()
		write(fpSample, file_object.all_content)
		close(fpSample)
		self.mark_path_for_removal(samplePath)

		# create a unique task ID
		taskName = "scaggr_task_{0}".format(split(samplePath)[1])

		# create On-Demand Scan (ODS):
		call(['sudo',
		      self._engine_path,
		      '--create-task', "'{0}'".format(taskName),
		      '--use-task-type=ODS'
		     ], stdout=fhNULL, stderr=fhNULL)

		# configure the ODS
		call(['sudo',
		      self._engine_path,
		      '--set-settings', "'{0}'".format(taskName),
		      '-N',
		      'ScanScope.ScanSettings.InfectedFirstAction=skip',
		      'ScanScope.AreaPath.Path={0}'.format(samplePath)
		     ], stdout=fhNULL, stderr=fhNULL)

		# create burnable XML output file, run the ODS, write to output file
		(fhXML, xmlPath) = tempfile.mkstemp()
		close(fhXML)
		call(['sudo',
		      self._engine_path,
		      '--start-task', "'{0}'".format(taskName),
		      '-N', '-W', '-F',
		      xmlPath
		     ], stdout=fhNULL, stderr=fhNULL)
		self.mark_path_for_removal(xmlPath)

		# read in result XML
		with open(xmlPath, "rb") as fp:
			scan_result = fp.read()

		# delete the task
		call(['sudo',
		      self._engine_path,
		      '--delete-task', "'{0}'".format(taskName),
		      '-N'
		     ], stdout=fhNULL, stderr=fhNULL)

		fhNULL.close()

		return scan_result

	def _parse_scan_result(self, scan_result):

		# TODO: make this fail-safe
		# Check specifically for "Completed" event and if no "ThreatDetected"
		# is found, but a Completed" is found, then infected is False

		infected, infected_string, metadata = False, '', dict()
		metadata.update(self.version)

		# Kaspersky generates an XML output that Python's minidom does not think is valid.  Specifically, the
		# Kaspersky format does not have a single root element, rather has an abritrary number of root <Event>
		# elements.  Here we inject a <pseudoRoot> element into the XML blob so that minidom handles properly.
		scan_result_pre = scan_result[:len('<?xml version="1.0" encoding="UTF-8"?>')]
		scan_result_post = scan_result[len('<?xml version="1.0" encoding="UTF-8"?>'):]
		scan_result = "{0}\n<pseudoRoot>{1}</pseudoRoot>".format(scan_result_pre, scan_result_post)

		# we're given a .xml buffer containing results
		domResults = parseString(scan_result)
		root = domResults.documentElement

		# find all Events s.t. Event.EventType == "ThreatDetected"
		for event in root.getElementsByTagName("Event"):

			# there should be exactly 1 eventType
			eventType = event.getElementsByTagName("EventType")[0]
			if eventType.firstChild.data != "ThreatDetected":
				continue

			infected = True
			infected_string = event.getElementsByTagName("root")[0].getElementsByTagName("ThreatName")[0].firstChild.data
			metadata['VerdictType'] = event.getElementsByTagName("root")[0].getElementsByTagName("VerdictType")[0].firstChild.data
			metadata['DangerLevel'] = event.getElementsByTagName("root")[0].getElementsByTagName("DangerLevel")[0].firstChild.data
			metadata['DetectCertainty'] = event.getElementsByTagName("root")[0].getElementsByTagName("DetectCertainty")[0].firstChild.data

			break

		return infected, infected_string, metadata
