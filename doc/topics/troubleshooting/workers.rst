===========================
Troubleshooting the Workers
===========================

Troubleshooting the workers.

Errors
======

Worker VM Out of Memory
-----------------------

There are a number of reasons why a worker VM could be out of memory.

* One of the Engines could have a memory leak.
* The Celery service might be running in DEBUG mode.
* There are other reasons.

First, check to see if the Celery service is running in DEBUG mode.
If you are running Celery on the command line, it is the ``-l`` flag.
If you are running Celery as a service, look in /etc/default/celeryd for the ``CELERYD_LOG_LEVEL`` parameter.
In production, it should be ``INFO``.
If you change the logging level, restart the Celery service.

If Celery is not the problem, just reboot that worker VM.

