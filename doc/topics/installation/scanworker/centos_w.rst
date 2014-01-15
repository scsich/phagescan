.. this file replaces /installation/scanworker/INSTALL.CentOS

Build a CentOS ScanWorker
=========================

0. If you haven't completed [Project_root_dir]/INSTALL, complete the
instructions listed there first.

Unless otherwise specified, assume the commands listed here are to be executed
from [Project_root_dir].

----

1. Install some base packages

This guide was developed against a CentOS 6 / RHEL 6 based system.
  CentOS 6.3 was installed with the "Minimal" option selected and then updated with sudo yum update.

NOTE: The vm/host must have 4GB of RAM or more. Else your later step to install the Symantec engine
  will fail!

Install commonly used packages (openssh-server is installed by default)

  $ su root
  $ yum install sudo openssh-clients acpid unzip htop bash-completion vim-enhanced

----

2. Create user named 'avuser'

  $ sudo adduser -U avuser

----

3. Install python 2.7

  $ sudo yum groupinstall "Development tools"
  $ sudo yum install zlib-devel bzip2-devel openssl-devel ncurses-devel
  $ curl -O http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tar.bz2
  $ tar xjf Python-2.7.3.tar.bz2
  $ cd Python-2.7.3
  $ ./configure --prefix=/usr/local
  $ sudo make &&  sudo make altinstall
  $ cd ..
  $ curl -O http://pypi.python.org/packages/source/d/distribute/distribute-0.6.32.tar.gz
  $ tar xzf distribute-0.6.32.tar.gz
  $ cd distribute-0.6.32
  $ sudo /usr/local/bin/python2.7 setup.py install
  $ sudo /usr/local/bin/easy_install-2.7 virtualenv

----

4. Create virtualenv

Become root for the next several steps.

  $ sudo su root

  $ /usr/local/bin/virtualenv-2.7 /opt/psvirtualenv

Activate Virtual Environment for this session

  $ source /opt/psvirtualenv/bin/activate

----

5. Install python packages into virtualenv

NOTE: do in activated virtualenv as root

  $ pip install $(< [Project_root_dir]/installation/scanworker/PACKAGES.pip)
  $ pip install --upgrade celery

----

6. Set avuser as owner and group for PhageScan code.

  $ chown -R avuser:avuser [Project_root_dir]

----

7. Install celery config.

  $ cd [Project_root_dir]
  $ cp installation/scanworker/workerceleryconfig.py workerceleryconfig.py
  $ chmod 640 workerceleryconfig.py

Edit workerceleryconfig.py as necessary.  In particular, tailor BROKER_CONF to your environment.

Now, if you are still the root user, revert back to a non-root user

----

8. Install chosen engines.

Currently, only the Symantec engine is supported on CentOS

Refer to the following files:
[Project_root_dir]/engines/[engine_name]/INSTALL

----

9. Start the scan worker (celery worker).

  $ cd [Project_root_dir]
  $ sudo su avuser
  $ source /opt/psvirtualenv/bin/activate
  $ celeryd -E -l DEBUG -Q symantec --hostname=worker.centos
