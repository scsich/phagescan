================
Phagescan Master
================

The Phagescan Master is the front-end and includes the following services:
  Django, Celery, RabbitMQ, PostgreSQL, Nginx, Gunicorn, and Supervisord.

Django
    Runs the Phagescan UI and Admin UI on localhost.
Celery
    The tasking system that communicates with the workers.
RabbitMQ
    The broker between the master and worker celery tasks.
PostgreSQL
    The database used by Django.
Nginx
    The external-facing service that proxies requests to Django.
Gunicorn
    Used to start Django automatically.
Supervisord
    Used to start CeleryCAM automatically.


Starting/Stopping All Django and Celery Services
================================================

The script ``dev/ps_services.sh`` can be used to start, stop, restart all of the Master Django and Celery services at one time.

Start
-----

Assuming the RabbitMQ service is running and configured, you can start Django and Celery as follows::

    sudo rabbitmqctl start_app
    sudo dev/ps_services.sh start

Stop
----

You can stop the Django and Celery services and the RabbitMQ app as follows::

    sudo dev/ps_services.sh stop
    sudo rabbitmqctl stop_app


Restart
-------

You can restart the Django and Celery services and reset the RabbitMQ app as follows::

    sudo dev/ps_services.sh stop
    sudo rabbitmqctl stop_app
    sudo rabbitmqctl start_app
    sudo dev/ps_services.sh start

This can be helpful to reset the Celery queues.


Django
======

Django can be started manually or with startup scripts.
During development it is best to start it manually.
A production environment will use the startup scripts.

Either way, Django should **only listen on localhost**.
To access Phagescan from outside the host, Nginx is used as a proxy.

Manual Start/Stop
-----------------

Run as same user that you used to start the 3 celeryd processes::

    [avuser@host]$ python manage.py runserver -v 3 127.0.0.1:9000 --settings=scaggr.settings

Stop it with CTRL+C.

Automated Start/Stop
--------------------

In Phagescan, we use ``gunicorn`` to automatically start Django on boot.

Start with::

    $ sudo service gunicorn start

Stop with::

    $ sudo service gunicorn stop

See installation/salt-masterless/salt/gunicorn for sample configuration files and startup script.

Accessing
---------

Access the Phagescan Web User Interfaces at::

    http://127.0.0.1:9000
    http://127.0.0.1:9000/admin

Celery
======

The Scan Master has 4 different Celery services running at the same time.

1. CeleryCAM - this is only used in production
2. Periodic Runner - run periodic tasks
3. Result Collector - collect results from workers
4. Master Task - manage tasks and send tasks to workers

Services 2-4 require a celery config file to be located in the [Project_root_dir].
The CeleryCAM uses a config file withing the /etc/supervisor/conf.d/ directory.

Manual Start/Stop
-----------------

Start the 3 celery processes each in separate terminals::

    [avuser@host]$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=masterceleryconfig -E -B -l info --hostname=master.master
    [avuser@host]$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=resultsceleryconfig -E -B -l info --hostname=master.results
    [avuser@host]$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=periodicceleryconfig -E -B -l info --hostname=master.periodic

Stop them with CTRL+C.

If you want debug output, change the ``-l info`` to ``-l debug``.

Automated Start/Stop
--------------------

In Phagescan, we use Celeryd startup scripts and ``supervisord`` to start the 4 Celery services automatically.

Start with::

    $ sudo service celeryd-master start
    $ sudo service celeryd-periodic start
    $ sudo service celeryd-result start
    $ sudo service supervisord start

Stop with::

    $ sudo service celeryd-master stop
    $ sudo service celeryd-periodic stop
    $ sudo service celeryd-result stop
    $ sudo service supervisord stop

See installation/salt-masterless/salt/[celery/master | supervisord] for sample configuration files and startup script.

RabbitMQ
========

RabbitMQ is installed as an Ubuntu package and will start automatically on boot, by default.
For Phagescan, all we need to do is add users, permissions, and vhosts for Celery to use.

Adding Users, Permissions, and Vhosts
-------------------------------------

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


Deleting Users, Permissions, and Vhosts
---------------------------------------

You delete the user and vhost and the permissions are automatically deleted.

::

    $ sudo rabbitmqctl del_user phagemasteruser
    $ sudo rabbitmqctl del_user phageworkeruser
    $ sudo rabbitmqctl del_vhost phage

Starting the RabbitMQ Application
---------------------------------

You only have to do this if you've manually stopped the application.
Starting the RabbitMQ service does this automatically.

::

    $ sudo rabbitmqctl start_app

Stopping the RabbitMQ Application
---------------------------------

This is how you would clear/delete the Celery Queues from RabbitMQ after you stop the Celery services::

     $ sudo rabbitmqctl stop_app

Examining the Queues
--------------------

RabbitMQ is the broker for the Celery queues, so you can examine many details about the Celery queues using ``rabbitmqctl``.
See the rabbitmqctl documentation for guidance.

One of the more useful commands is::

    $ sudo rabbitmqctl -p phage list_queues name consumers messages

This will list all of the queues on the phage vhost; specifically the name, number of consumers, and number of messages
for each queue.

PostgreSQL
==========

Configure
---------

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

Starting/Stopping
-----------------

This is a standard service, so start and stop by doing::

    $ sudo service postgresql start

    $ sudo service postgresql stop


Nginx
=====

A default Nginx config file is provided in installation/salt-masterless/salt/nginx/.
Once it is configured, you can start or stop the nginx service as follows::

    $ sudo service nginx start

    $ sudo service nginx stop

Note: after changing the configuration file, you should restart the service.

