"""
As stated in installation/salt-masterless/README, several directories
must be created prior to running salt states on a masterless vagrant VM.
i.e. you should not run vagrant up until you've completed those prep steps.

This script will do that for you.

usage: python vagrant_prep.py


For the PILLAR, MEDIA, and LICENSES in the conf dictionary:
DST_PATH - path relative to PROJECT_ROOT where the directory will be created.
SRC_PATH - source of directory to copy to DST_PATH
	''                                  - no source directory, create DST_PATH
	'/path/to/local/dir'                - copy local directory to DST_PATH; absolute path or relative to PROJECT_ROOT
	'ssh://git@example.com/myfiles.git' - clone git repo to DST_PATH
SRC_TYPE - type of source path
	'none'                              - SOURCE is ''
	'directory'                         - SOURCE is a local directory
	'git'                               - SOURCE is a git repo

"""
import os
import shutil
import subprocess


conf = {
	'PROJECT_ROOT': {
		'NAME': 'phagescan',
		'PATH': '', # path will be dynamically resolved upon execution
	},
	'PILLAR': {
		'NAME': 'pillar',
		'DST_PATH': 'installation/salt-masterless/pillar',
		'SRC_PATH': 'installation/salt-masterless/pillar-sample', # absolute path or relative to PROJECT_ROOT
		'SRC_TYPE': 'local', # 'none', 'local', or 'git'
	},
	'MEDIA': {
		'NAME': 'install-media',
		'DST_PATH': 'installation/install-media',  # relative to PROJECT_ROOT
		'SRC_PATH': '/home/nick/Documents/narf/MassScan/installation/install-media', # absolute path or relative to PROJECT_ROOT
		'SRC_TYPE': 'local', # 'none', 'local', or 'git'
	},
	'LICENSES': {
		'NAME': 'licenses',
		'DST_PATH': 'installation/licenses', # relative to PROJECT_ROOT
		'SRC_PATH': 'ssh://narfgitrepo/mass-scan-licenses-bt.git', # absolute path or relative to PROJECT_ROOT
		'SRC_TYPE': 'git', # 'none', 'local', or 'git'
	},
	'WORKER': {
		'NAME': 'scanworker',
		'DST_PATH': 'installation/install-media/scan_worker',
		'SRC_PATH': 'scan_worker.zip',
		'SCRIPT_PATH': 'installation/scanworker',
		'SCRIPT_NAME': 'make_scanworker_zip.sh',
	},
	'MASTER': {
		'NAME': 'scanmaster',
		'DST_PATH': 'installation/install-media/scan_task_master',
		'SRC_PATH': 'scan_master.zip',
		'SCRIPT_PATH': 'installation/scanmaster',
		'SCRIPT_NAME': 'make_scanmaster_zip.sh',
	},
	'CELERY': {
		'NAME': 'celeryconfigs',
		'WORKER_PATH': 'installation/scanworker/workerceleryconfig.py',
		'MASTER_PATH': 'installation/scanmaster/masterceleryconfig.py',
		'PERIODIC_PATH': 'installation/scanmaster/periodicceleryconfig.py',
		'RESULTS_PATH': 'installation/scanmaster/resultsceleryconfig.py',
	}
}


def find_and_set_project_root_path():
	dir_split = os.path.split(os.getcwd())
	if dir_split[1] == 'dev':
		conf['PROJECT_ROOT']['PATH'] = dir_split[0]
	elif dir_split[1] == conf['PROJECT_ROOT']['NAME']:
		conf['PROJECT_ROOT']['PATH'] = os.getcwd()
	else:
		raise OSError('This script must be run from {0}/ or {0}/dev/.'.format(conf['PROJECT_ROOT']['NAME']))


def _make_dir(dir_type):
	abs_dst_path = dir_type['DST_PATH']
	if not os.path.exists(abs_dst_path):
		abs_dst_path = os.path.join(conf['PROJECT_ROOT']['PATH'], abs_dst_path)

	if dir_type['SRC_TYPE'] == 'local':
		# copy src to dst
		abs_src_path = dir_type['SRC_PATH']
		if not os.path.exists(abs_src_path):
			abs_src_path = os.path.join(conf['PROJECT_ROOT']['PATH'], abs_src_path)
		if not os.path.exists(abs_src_path):
			raise IOError('Invalid source path. Neither absolute path nor relative path exist.')
		print "Copying directory '{0}' to '{1}'.".format(abs_src_path, abs_dst_path)
		shutil.copytree(abs_src_path, abs_dst_path)
	else:
		# make dst dir
		print "Making directory '{0}'.".format(abs_dst_path)
		os.mkdir(abs_dst_path, 0775)


def _clone_repo(dir_type):
	try:
		from git import Repo
	except ImportError:
		raise ImportError("Using git requires 'GitPython' python module. Install it an try again.")

	abs_dst_path = dir_type['DST_PATH']
	if not os.path.exists(abs_dst_path):
		abs_dst_path = os.path.join(conf['PROJECT_ROOT']['PATH'], abs_dst_path)
	repo_path = dir_type['SRC_PATH']
	print "Cloning repo '{0}' into '{1}.".format(repo_path, abs_dst_path)
	new_repo = Repo.clone_from(repo_path, abs_dst_path)


def process_dir(dir_type):
	full_path = os.path.join(conf['PROJECT_ROOT']['PATH'], dir_type['DST_PATH'])
	#print "\n{0} -> '{1}'".format(dir_type['NAME'], full_path)

	if os.path.exists(full_path):
		print 'Nothing to do for {0}; directory exists.'.format(dir_type['NAME'])
	else:
		#print 'Creating {0} directory.'.format(dir_type['NAME'])
		if dir_type['SRC_TYPE'] == 'git':
			_clone_repo(dir_type)
		else:
			_make_dir(dir_type)


def update_source_code_archives(archive_type):

	dst_path = os.path.join(conf['PROJECT_ROOT']['PATH'], archive_type['DST_PATH'])
	src_path = os.path.join(conf['PROJECT_ROOT']['PATH'], archive_type['SRC_PATH'])
	script_path	= os.path.join(conf['PROJECT_ROOT']['PATH'], archive_type['SCRIPT_PATH'])

	#print "DST: {0}, {1}".format(dst_path, os.path.exists(dst_path))
	#print "SRC: {0}, {1}".format(src_path, os.path.exists(src_path))
	#print "SCRIPT: {0}, {1}".format(script_path, os.path.exists(os.path.join(script_path, archive_type['SCRIPT_NAME'])))

	# TODO: use native python git/zip modules instead of calling out to shell scripts.
	subprocess.call(os.path.join('.', archive_type['SCRIPT_NAME']), cwd=script_path)

	print "Moving archive to {0}".format(dst_path)
	shutil.copy(src_path, dst_path)
	os.unlink(src_path)


def place_celery_configs():
	print "Copying celery configs to PROJECT_ROOT."
	dst_path = conf['PROJECT_ROOT']['PATH']
	for celery_file_path in ['WORKER_PATH', 'MASTER_PATH', 'PERIODIC_PATH', 'RESULTS_PATH']:
		full_path = os.path.join(conf['PROJECT_ROOT']['PATH'], conf['CELERY'][celery_file_path])
		#print "Copying {0} to {1}".format(full_path, dst_path)
		if os.path.exists(os.path.join(dst_path, os.path.split(conf['CELERY'][celery_file_path])[1])):
			print "Nothing to do for {0}; file exists.".format(celery_file_path)
		else:
			shutil.copy(full_path, dst_path)
	print "Be sure to update BROKER_CONF values in workerceleryconfig.py."


if __name__ == '__main__':
	find_and_set_project_root_path()
	#print "Project root -> '{0}'".format(conf['PROJECT_ROOT']['PATH'])

	# create main directories
	for dir_type_val in ['PILLAR', 'MEDIA', 'LICENSES']:
		process_dir(conf[dir_type_val])

	# update scanmaster and scanworker archives in install-media
	for archive_type_val in ['WORKER', 'MASTER']:
		update_source_code_archives(conf[archive_type_val])

	# copy master and worker celery configs to PROJECT_ROOT
	place_celery_configs()