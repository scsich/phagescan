.. this file replaces /installation/dev/INSTALL

Manually Build Development VM
=============================

These instructions are for manually building/configuring a development host.
If you are using vagrant, refer to INSTALL.vagrant-salt.


0. If you haven't completed [Project_root_dir]/INSTALL, complete the
instructions listed there first.

The following instructions assume execution within the virtualenv established
in the root INSTALL document.

Unless otherwise specified, assume the commands listed here are to be executed
from [Project_root_dir].

----

1-3. Complete steps 1 through 3 from:
[Project_root_dir]/installation/scanmaster/INSTALL

----

3. Start host services.

If running Ubuntu:
$ sudo /etc/init.d/rabbitmq-server start
$ sudo /etc/init.d/postgresql start

If running CentOS:
TODO

----

4. Set up rabbitmq.

$ sudo rabbitmqctl add_user test test
$ sudo rabbitmqctl add_vhost phage
$ sudo rabbitmqctl set_permissions -p phage test ".*" ".*" ".*"

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

6. Resolve 'scanmaster' to localhost.

$ sudo su
# echo "127.0.0.1 scanmaster" >> /etc/hosts
# exit

----

7. Create Django database tables & superuser.

$ python manage.py syncdb --settings=scaggr.settings_dev

This should prompt if you wish to create a django superuser.  You do; define
devuser/devpass.  Give a fake e-mail addr.
$ python manage.py migrate --settings=scaggr.settings_dev

Collect static files
$ python manage.py collectstatic

----

8. Install the scanner engines you wish to test.

Refer to the following files:
[Project_root_dir]/engines/[engine_name]/INSTALL

NOTE: Since we're only setting up a development environment, ignore any
'avuser' instructions.  We will not create this user.

----

9. Start the master & worker celery daemons (execute each of these in a new
shell so errors are easily apparent):
$ DJANGO_SETTINGS_MODULE=scaggr.settings_dev celeryd --config=masterceleryconfig -E -B -l INFO -n master
$ DJANGO_SETTINGS_MODULE=scaggr.settings_dev celeryd --config=resultsceleryconfig -E -B -l INFO -n master-results
$ celeryd --config=workerceleryconfig -E -l INFO -n worker

NOTE: Each shell instance must be within the virtualenv previously configured.

----

10. Start the django development web server, log in with the previously created
superuser:
$ python manage.py runserver -v 3 0.0.0.0:8000 --settings=scaggr.settings_dev

----

DEBUGGING:

If you're experiencing weird DB-related issues, drop and re-add the DB.
It might be some latent problem.
$ [Project_root_dir]/dev/dev_reset_db.sh

Or, if you prefer, reset the DB and remove all uploaded samples and MD
engine-generated files:
$ [Project_root_dir]/dev/dev_reset_all.sh

NOTE: these scripts will require sudo ability to the postgres user.

