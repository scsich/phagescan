.. this file replaces /installation/scanworker/ISNTALL.Ubuntu

==========================
Build an Ubuntu ScanWorker
==========================


0. If you haven't completed [Project_root_dir]/INSTALL, complete the
instructions listed there first.

The following instructions assume execution within the virtualenv established
in the root INSTALL document.

Unless otherwise specified, assume the commands listed here are to be executed
from [Project_root_dir].

If you are on a production host, run commands as user 'avuser'.

----

1. Install necessary Python packages.

$ sudo pip install $(< [Project_root_dir]/installation/scanworker/PACKAGES.pip)

----

2. Get latest version of celery 3.0.x.

$ sudo pip install --upgrade celery==3.0.24

----

3. Copy the appropriate config file to the Project_root_dir and rename it celeryconfig.py.

$ cp installation/scanworker/workerceleryconfig.py workerceleryconfig.py

----

4. Edit workerceleryconfig.py as necessary.  In particular, tailor BROKER_CONF to your environment.

----

5. Install chosen engines.

Refer to the following files:
[Project_root_dir]/engines/[engine_name]/INSTALL

----

6. Start a worker

To start a scan worker from the root project directory:
$ celeryd -l DEBUG -E --config=workerceleryconfig --hostname=worker.ubuntu

----

7. Start celery on boot

Use the init.d/default scripts located in the salt state tree.
