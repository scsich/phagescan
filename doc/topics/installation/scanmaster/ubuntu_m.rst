============================
Manually Build a Scan Master
============================

These instructions are for manually building/configuring a scan master host,
instead of using Vagrant/Salt to build a VM.
This must be an Ubuntu host.
This is how you would manually build a production scan master. It is only lacking the automated startup scripts
for celery and django.

If you are building a production scan master, you should create a user specifically to run Phagescan and then run everything
as that user.
We use the user `avuser` by default.
If this is not for a production scan master, you can select a user of your choice.

Prepare your Environment
========================

Create user `avuser` and set a password::

    $ sudo adduser -U avuser
    $ sudo passwd avuser

Clone the GitHub repo, move it into /opt, and set ownership::

    $ git clone git@github.com:scsich/phagescan.git
    $ sudo mv phagescan /opt/
    $ sudo chown -R avuser:avuser /opt/phagescan

You now have a `/opt/phagescan` directory, which we will refer to as [Project_root_dir].

Install necessary OS packages::

    If running Ubuntu:
    $ sudo apt-get install $(< [Project_root_dir]/PACKAGES.ubuntu)
    $ sudo apt-get install $(< [Project_root_dir]/installation/scanmaster/PACKAGES.ubuntu)

Build & activate a virtual environment::

    $ sudo su
    $ virtualenv --setuptools /opt/psvirtualenv
    [root@host]$ source /opt/psvirtualenv/bin/activate

Your prompt should look like this after::

    (psvirtualenv)[root@host]$

If you need to deactivate the virtual env (don't do this now)::

    (psvirtualenv)[root@host]$ deactivate

Install Python requirements into Virtualenv::

    (psvirtualenv)[root@host]$ pip install -r [Project_root_dir]/installation/scanmaster/PACKAGES.pip

You are done with the root user, so return to your standard user::

    (psvirtualenv)[root@host]$ exit

If not already running, start rabbitmq and postgresql::

    $ sudo /etc/init.d/rabbitmq-server start
    $ sudo /etc/init.d/postgresql start

Configuration
=============

Unless otherwise specified, assume the commands listed here are to be executed from [Project_root_dir].

Set up rabbitmq:

Replace the username and password with the credentials that you would like to use and run the following commands::

    $ sudo rabbitmqctl add_user phagemasteruser longmasterpassword
    $ sudo rabbitmqctl add_user phageworkeruser longworkerpassword
    $ sudo rabbitmqctl add_vhost phage
    $ sudo rabbitmqctl set_permissions -p phage phagemasteruser ".*" ".*" ".*"
    $ sudo rabbitmqctl set_permissions -p phage phageworkeruser ".*" ".*" ".*"

* If the master and worker hosts use different user/pass combinations to
  communicate with the broker, you must use the commands as written above.
  However, if the master and worker hosts use the same user/pass, you may add one
  user and set_permissions on that one user. In that case, there is no need for the second user.
  A production system should use separate credentials for the master and workers.

* Note: These credentials are the BROKER_CONF for the master and workers.
  So, make sure the username and password you created here are set in both the master and worker BROKER_CONFs::

      For the master it is in scaggr/settings.py.
      For the worker it is in workerceleryconfig.py.

Set up postgres:

Replace the username and password with the credentials that you would like to use and run the following commands::

    $ sudo su postgres
    $ psql
    postgres=# create user citestsuper createdb superuser password 'sup3rdup3r';
    postgres=# create database phage owner citestsuper;
    postgres=# \q
    $ psql -d phage
    phage=# create extension hstore;
    phage=# \q
    $ exit

The remaining configuration should be done as user `avuser`, so switch now::

    $ sudo su avuser

Create Django database tables, cache and superuser::

    [avuser@host]$ python manage.py syncdb --settings=scaggr.settings
    [avuser@host]$ python manage.py migrate --settings=scaggr.settings
    [avuser@host]$ python manage.py createcachetable --settings=scaggr.settings cache

* Note: The first command prompts you to create a django superuser.  Do so and use a strong password.
  For development define devuser/devpass.  Give a fake e-mail addr.

Copy the appropriate config files to [Project_root_dir]::

    [avuser@host]$ cp installation/scanmaster/masterceleryconfig.py masterceleryconfig.py
    [avuser@host]$ cp installation/scanmaster/resultsceleryconfig.py resultsceleryconfig.py
    [avuser@host]$ cp installation/scanmaster/periodicceleryconfig.py periodicceleryconfig.py

Collect Static files::

    [avuser@host]$ python manage.py collectstatic

Start the celery processes each in separate terminals::

    [avuser@host]$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=masterceleryconfig -E -B -l info --hostname=master.master
    [avuser@host]$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=resultsceleryconfig -E -B -l info --hostname=master.results
    [avuser@host]$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=periodicceleryconfig -E -B -l info --hostname=master.periodic

Start the django development web server::

    Run as same user that you used to start the 3 celeryd processes.
    [avuser@host]$ python manage.py runserver -v 3 127.0.0.1:8000 --settings=scaggr.settings

You can now access the Phagescan Web User Interface::

    http://127.0.0.1:8000
    http://127.0.0.1:8000/admin

Optional production extras:

* To automatically start celeryd processes, you can use init.d scripts. See installation/salt-masterless/salt/celery for reference versions.
* To automatically start django on boot, you can use gunicorn or supervisord.
* In production, you should have a full webserver in front of Django: apache or nginx.
* In production, you should enable the EngineActiveMarkerTask periodic task in virusscan/tasks.py.
* Also, schedule update_definitions to run periodically. virusscan/models.py:ScannerType.update_definitions().
