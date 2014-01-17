====================================
Manually Build an Ubuntu Scan Worker
====================================

These instructions are for manually building/configuring an Ubuntu scan worker host (or VM),
instead of using Vagrant/Salt to build a VM.
This is how you would manually build a production scan worker. It is only lacking the automated startup scripts
for celery.

If you are building a production scan worker, you should create a user specifically to run Phagescan and then run everything
as that user.
We use the user `avuser` by default.

Prepare your Environment
========================

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
    $ sudo apt-get install $(< [Project_root_dir]/PACKAGES.ubuntu)

Build & activate a virtual environment::

    $ sudo su
    $ virtualenv --setuptools /opt/psvirtualenv
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

Start the Celery worker process
===============================

Use the following command to manually start celeryd::

    (psvirtualenv)[avuser@host]$ celeryd -l INFO -E --config=workerceleryconfig --hostname=worker.ubuntu

To start celery on boot, see the init.d/default scripts located in the salt state tree.
See installation/salt-masterless/salt/celery/worker for reference versions.
