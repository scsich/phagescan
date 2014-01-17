=============================
Manually Build Development VM
=============================

These instructions are for manually building/configuring a development host that is both a scanmaster and scanworker,
instead of using Vagrant/Salt to build a `phagedev` VM.
This must be an Ubuntu host.

Prequisites
===========

Start by following the steps to :doc:`Prepare your Environment </topics/development/index>`.
Specifically, you want to complete the steps to `Setup Git` and `Local Python SDK in VirtualEnv on development host`.

If not already running, start rabbitmq and postgresql::

    $ sudo /etc/init.d/rabbitmq-server start
    $ sudo /etc/init.d/postgresql start


Configuration
=============

Unless otherwise specified, assume the commands listed here are to be executed from [Project_root_dir].

Set up rabbitmq::

    $ sudo rabbitmqctl add_user test test
    $ sudo rabbitmqctl add_vhost phage
    $ sudo rabbitmqctl set_permissions -p phage test ".*" ".*" ".*"

Set up postgres::

    $ sudo su postgres
    $ psql
    postgres=# create user citestsuper createdb superuser password 'sup3rdup3r';
    postgres=# create database phage owner citestsuper;
    postgres=# \q
    $ psql -d phage
    phage=# create extension hstore;
    phage=# \q
    $ exit

Resolve 'scanmaster' to localhost::

    $ sudo su
    # echo "127.0.0.1 scanmaster" >> /etc/hosts
    # exit

Install the scanner engines you wish to test.

    * Refer to the following files::

      [Project_root_dir]/engines/[engine_name]/INSTALL

    * NOTE: Since we're only setting up a development environment, ignore any 'avuser' instructions.  We will not create this user.

For the Master, you need to configure and start Django and 3 celery workers.

Create Django database tables, cache, and superuser.

  The first command will prompt you to create a django superuser.  Do so.
  Use devuser/devpass and give a fake e-mail addr::

    $ cd [Project_root_dir]
    $ source /opt/psvirtualenv/bin/activate
    (psvirtualenv)$ python manage.py syncdb --settings=scaggr.settings
    (psvirtualenv)$ python manage.py migrate --settings=scaggr.settings
    (psvirtualenv)$ python manage.py createcachetable --settings=scaggr.settings cache

Copy the appropriate Celery config files to the [Project_root_dir]::

    (psvirtualenv)$ cp installation/scanmaster/masterceleryconfig.py masterceleryconfig.py
    (psvirtualenv)$ cp installation/scanmaster/resultsceleryconfig.py resultsceleryconfig.py
    (psvirtualenv)$ cp installation/scanmaster/periodicceleryconfig.py periodicceleryconfig.py


Collect Static files::

    (psvirtualenv)$ python manage.py collectstatic

Update scaggr/settings.py.

* Set DEBUG is True
* Update the BROKER_CONF values to match the user and vhost values we configured in the rabbitmq step above.

Start the celery processes, each in separate terminals::

    (psvirtualenv)$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=masterceleryconfig -E -B -l info --hostname=master.master
    (psvirtualenv)$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=resultsceleryconfig -E -B -l info --hostname=master.results
    (psvirtualenv)$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=periodicceleryconfig -E -B -l info --hostname=master.periodic

Start the django development web server.

  Be sure to run django as same user that you used to start celeryd::

    (psvirtualenv)$ python manage.py runserver -v 3 0.0.0.0:8000 --settings=scaggr.settings

For the Worker, you only need to configure and start one celery worker. Copy the worker Celery config::

    (psvirtualenv)$ cp installation/scanworker/workerceleryconfig.py workerceleryconfig.py

Edit the Worker celery config and define the BROKER_CONF variables to match the those from the settings.py above.

Start the Celery Worker::

    (psvirtualenv)$ celeryd --config=workerceleryconfig -E -l INFO -n worker

Now we have the Django Web Interface listening on port 8000 on your host.
To connect to the Django Web User Interface::

    http://localhost:8000

Login to the Django Web User Interface with the django superuser user/password that you created.

You can reach the Admin interface by going to::

    http://localhots:8000/admin/

----

Some helpful tips:

* When you start Django for the first time, it will create a logs directory: [Project_root_dir]/logs. That is where
  celery and django logging is written.
* If you're experiencing weird DB-related issues, drop and re-add the DB. It might be some latent problem::

    $ [Project_root_dir]/dev/dev_reset_db.sh

* Or, if you prefer, reset the DB and remove all uploaded samples and MD engine-generated files::

    $ [Project_root_dir]/dev/dev_reset_all.sh

* NOTE: these scripts will require sudo ability to the postgres user.

