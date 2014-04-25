===================================
Manually Build a CentOS Scan Worker
===================================

These instructions are for manually building/configuring a CentOS scan worker host (or VM),
instead of using Vagrant/Salt to build a VM.
This is how you would manually build a production scan worker. It is only lacking the automated startup scripts
for celery.

If you are building a production scan worker, you should create a user specifically to run Phagescan and then run everything
as that user.
We use the user `avuser` by default.

This guide was developed against a CentOS 6 / RHEL 6 based system.
CentOS 6.3 was installed with the "Minimal" option selected and then updated with ``yum update``.
CentOS 6.4 has been tested successfully as well.

NOTE: The vm/host **must have 4GB of RAM** or more, else your later step to install the Symantec engine will fail!

Prepare your Environment
========================

Install commonly used packages (openssh-server is installed by default)::

    $ su root
    [root@host]$ yum install sudo openssh-clients acpid unzip htop bash-completion vim-enhanced
    [root@host]$ exit

Now we can use `sudo`.

Create user `avuser` and set a password::

    $ sudo adduser -U avuser
    $ sudo passwd avuser

On the scan master, create scan_worker.zip by using the script::

    installation/scanworker/make_scanworker_zip.sh

Transfer that .zip file from the scan master to this host.

Unzip the scan_master.zip, move it into /opt, and set ownership::

    $ unzip scan_master.zip
    $ sudo mv phagescan /opt/
    $ sudo chown -R avuser:avuser /opt/phagescan

You now have a `/opt/phagescan` directory, which we will refer to as [Project_root_dir].

Install necessary OS packages::

    If running Ubuntu:
    $ sudo apt-get install $(< [Project_root_dir]/PACKAGES.centos)


Unless otherwise specified, assume the commands listed here are to be executed
from [Project_root_dir].

Install python 2.7::

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

Build & activate a virtual environment::

    $ sudo su
    $ /usr/local/bin/virtualenv-2.7 --setuptools /opt/psvirtualenv
    [root@host]$ source /opt/psvirtualenv/bin/activate

Your prompt should look like this after::

    (psvirtualenv)[root@host]$

If you need to deactivate the virtual env (don't do this now)::

    (psvirtualenv)[root@host]$ deactivate

Install Python requirements into Virtualenv::

    (psvirtualenv)[root@host]$ pip install -r [Project_root_dir]/installation/scanworker/PACKAGES.pip

You are done with the root user, so return to your standard user, su to avuser and activate virtual env::

    (psvirtualenv)[root@host]$ exit
    $ sudo su avuser
    $ source /opt/psvirtualenv/bin/activate

Copy the Celery config file to the [Project_root_dir]::

    (psvirtualenv)[avuser@host]$ cp installation/scanworker/workerceleryconfig.py workerceleryconfig.py

Edit workerceleryconfig.py as necessary.  In particular, tailor BROKER_CONF to your environment.

Install chosen engines
======================

Refer to the following files::

  [Project_root_dir]/engines/[engine_name]/INSTALL

* Currently, only the Symantec engine is supported on CentOS

Start the Celery worker process
===============================

Use the following command to manually start celeryd::

    (psvirtualenv)[avuser@host]$ celeryd -l INFO -E --config=workerceleryconfig --hostname=worker.centos

To start celery on boot, see the init.d/default scripts located in the salt state tree.
See installation/salt-masterless/salt/celery/worker for reference versions.

