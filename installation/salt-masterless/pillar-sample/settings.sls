# Where the phagescan code can be found. [Project_root_dir]
# Default to the shared directory root that vagrant
# mounts inside a vagrant vm.
# For production systems use /opt/phagescan
#ps_root: /opt/phagescan
ps_root: /vagrant

# The directory where the virtual env will be created
# and where all python packages will be installed.
virt_env_dir: /opt/psvirtualenv

# The env from where install media pkgs are pulled
media_env: media

# The env where license files are pulled
lic_env: lic

####### PHAGESCAN SOURCE CODE ############
scan_worker_pkg: scan_worker.zip
scan_worker_dir_name: phagescan
scan_task_master_pkg: scan_master.zip
scan_task_master_dir_name: phagescan

########## SERVERS #####################
# Used by postgresql-server/init.sls
# Used by settings.py
phage_scan_db_name: phage
phage_scan_db_user_name: citestsuper
phage_scan_db_user_passwd: sup3rdup3r

# Used by rabbitmq-server/init.sls
# Used by settings.py
# Used by master celery config(s)
mq_master_user_name: phagemasteruser
mq_master_user_passwd: longmasterpassword
# Should be equal to worker's vhost name
mq_master_vhost_name: phage

# Used by rabbitmq-server/init.sls
# Used by worker celery config
mq_worker_user_name: phageworkeruser
mq_worker_user_passwd: longworkerpassword
# Should be equal to master's vhost name
mq_worker_vhost_name: phage



########## LIBRARIES #####################
# Python 2.7 - for CentOS
python27_version: 2.7.3
python27_tarball: Python-2.7.3.tar.bz2
python27_sha256: 726457e11cb153adc3f428aaf1901fc561a374c30e5e7da6742c0742a338663c
python27_tarball_dirname: Python-2.7.3

# Distribute for Python 2.7 - for CentOS
distribute_tarball: distribute-0.6.32.tar.gz
distribute_sha256: 8970cd1e148b5d1fea9430584aea66c45ea22d80e0933393ec49ebc388f718df
distribute_tarball_dirname: distribute-0.6.32

# JRE - for Symantec on CentOS
jre_pkg: jre-7u25-linux-i586.rpm


########## ENGINES #####################
# List of engines and the variables to define:
#  engine: name of the engine's state file directory
#  name: name of first state in engine's init.sls file
#  type: type of first state in engine's init.sls file

ubuntu_engines:
  - engine: avast
    name: avast-reqts
    type: cmd
  - engine: avira
    name: avira-reqts
    type: cmd
  - engine: bitdefender
    name: bitdefender-reqts
    type: cmd
  - engine: clamav
    name: clamav-reqts
    type: cmd
  - engine: eset
    name: eset-reqts
    type: cmd
  - engine: kaspersky
    name: kaspersky-reqts
    type: cmd
  - engine: oms
    name: oms-pre-reqts
    type: cmd
  - engine: opaf
    name: opaf-reqts
    type: cmd
  - engine: pdfid
    name: pdfid-reqts
    type: cmd
  - engine: peid
    name: peid-reqts
    type: pip
  - engine: sophos
    name: sophos-reqts
    type: cmd
  - engine: yara
    name: yara-pre-req
    type: pip

centos_engines:
  - engine: symantec
    name: symantec-reqts
    type: cmd

# Variables for engine installation media

# Avast
avast_pkg: libavastengine-4.7.6-i586.deb
avastsrv_pkg: avast4server-3.2.1-i586.tar.gz
avastsrv_tardir_name: avast4server-3.2.1-i586
avast_lic: License.dat

# Avira
avira_pkg: antivir-server-prof.tar.gz
avira_tardir_name: antivir-server-prof-3.1.3.5-2
avira_lic: hbedv.key

# BitDefender
bitdefender_pkg: bitdefender-scanner_7.6-4_i386.deb
bitdefender_license: LICENSE

# Eset
eset_pkg: esets-4.0.10.amd64.deb
eset_lic: nod32.lic
eset_update_username: USER
eset_update_password: PASS

# Kaspersky
kaspersky_pkg: kes4lwks_8.0.1-50_i386.deb
kaspersky_key: kaspersky.key

# OfficeMalScan (oms)
oms_pkg: OfficeMalScanner.zip

# Sophos
sophos_pkg: linux.amd64.glibc.2.3.tar.Z
sophos_sig_pkg: 493_ides.zip

# Symantec
symantec_pkg: Symantec_Protection_Engine_NAS_7.0.2.4_Linux_IN.zip
symantec_pkg_dirname: SPE_NAS
symantec_lic: spe.slf
symantec_admin_pwd_hash: 27F23E30BA3516EE1EA84E8EE36CE19CA5ED495EEFC4D81CBBDFC925461C062C6146CC5F200C938A8C8549A38D9F0CECE581282671EA666C9C4ADF1272C7739058D089A6035CD570ACEDC3D94162A138

