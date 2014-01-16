.. this file replaces /installation/scanmaster/INSTALL

Building a ScanMaster VM
========================

These instructions walk you through manually building a scan master VM/host.


0. If you haven't completed [Project_root_dir]/INSTALL, complete the
instructions listed there first.

The following instructions assume execution within the virtualenv established
in the root INSTALL document.

Unless otherwise specified, assume the commands listed here are to be executed
from [Project_root_dir].

Also, we assume you are running the scanmaster on Ubuntu, so YMMV with other distros.

If you are working on a production host, you should be user 'avuser'.

----

1. Install necessary OS packages.

$ sudo apt-get install $(< [Project_root_dir]/installation/scanmaster/PACKAGES.ubuntu)

----

2. Install necessary Python packages.

$ sudo pip install -r [Project_root_dir]/installation/scanmaster/PACKAGES.pip

----

3. Start host services.

$ sudo /etc/init.d/rabbitmq-server start
$ sudo /etc/init.d/postgresql start

----

4. Set up rabbitmq.

Replace the user name and password with the credentials that you would like to
use and run the following commands:
$ sudo rabbitmqctl add_user phagemasteruser longmasterpassword
$ sudo rabbitmqctl add_user phageworkeruser longworkerpassword
$ sudo rabbitmqctl add_vhost phage
$ sudo rabbitmqctl set_permissions -p phage phagemasteruser ".*" ".*" ".*"
$ sudo rabbitmqctl set_permissions -p phage phageworkeruser ".*" ".*" ".*"

If the master and worker hosts use different user/pass combinations to
communicate with the broker, you must use the commands as written above.
However, if the master and worker hosts use the same user/pass, you may add one
user and set_permissions on that one user. There is no need for the second user.

----

5. Set up postgres.

$ sudo su postgres
$ psql
postgres=# create user citestsuper createdb superuser password 'sup3rdup3r';
postgres=# create database phage owner citestsuper;
postgres=# \q
$ psql -d phage
phage=# create extension hstore;
phage=# \q
$ exit

----

6. Create Django database tables & superuser.

$ python manage.py syncdb --settings=scaggr.settings

This should prompt if you wish to create a django superuser.  You do.
For development define devuser/devpass.  Give a fake e-mail addr.

$ python manage.py migrate --settings=scaggr.settings

This will create the table for the DatabaseCache
$ python manage.py createcachetable --settings=scaggr.settings cache

----

6. Copy the appropriate config files to the scaggr root.

$ cp installation/scanmaster/masterceleryconfig.py masterceleryconfig.py
$ cp installation/scanmaster/resultsceleryconfig.py resultsceleryconfig.py
$ cp installation/scanmaster/periodicceleryconfig.py periodicceleryconfig.py

----

7. Edit edit the three celery configs as necessary.

Generally, there is nothing to change.

----

8. Collect Static files.

$ python manage.py collectstatic

----

9. Start the celery processors (each in separate terminals).

To start a master processor from the root project directory:
$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=masterceleryconfig -E -B -l info --hostname=master.master

Start the results processor from the root project directory:
$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=resultsceleryconfig -E -B -l info --hostname=master.results

Start the periodic processor from the root project directory:
$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=periodicceleryconfig -E -B -l info --hostname=master.periodic

----

10. Start the django development web server.

Run as same user that you used to start celeryd.
$ python manage.py runserver -v 3 0.0.0.0:8000 --settings=scaggr.settings

----

11. Production extras

In production, you should enable the EngineActiveMarkerTask periodic task in virusscan/tasks.py.
Also, schedule update_definitions to run periodically. virusscan/models.py:ScannerType.update_definitions().
