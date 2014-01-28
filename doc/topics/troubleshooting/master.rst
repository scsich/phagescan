==========================
Troubleshooting the Master
==========================

Troubleshooting the master.

Where To Find Logs
==================

Celery and Django logs will be in one of these directories::

    /opt/phagescan/logs
    c:/phagescan/logs
    /var/log/celery/

RabbitMQ, Nginx, and PostgreSQL logs will be in::

    /var/log/

Rebooting The Master Host
=========================

If you are running everything on a single host, including OpenStack, for a production environment,
it can be complicated to do a controlled reboot.
This is not a common situation, but here is what you do:

First, you should shutdown/destroy all VM instances. Then you can do a standard reboot command.

0. Log into the Phagescan Status page and click the "X" icon next to one engine from each VM type to destroy the workers.
   (i.e. clicking the 'X' for Panda, Symantec, and Kaspersky will destroy all of the 3 types of VMs, because they each
   run on a different VM type).
1. Log into the OpenStack UI, go to the "Instances" page, and Force Destroy any instances in the "shutdown" state.
   **!!! DO NOT remove images from the Images or Snapshots pages !!!**
2. Properly reboot the master box::

    $ sudo shutdown -r now

3. Upon reboot, log into the Phagescan server status page and click the Up arrow next to one engine from each VM type
   to start up the workers. (i.e. clicking the up arrow for Panda, Symantec, and Kaspersky will start up the 3 types
   of VMs, because they each run on a different VM type).
4. Wait about 15 minutes for everything to stabilize.

Problems Starting Worker VMs After a Power Outage
=================================================

This problem arises because OpenStack only allows the number of VMs Instances as can be supported by physical hardware.
The odd thing is that it counts instances in the shutdown state.
When the power goes out and the host boots, all of the previously running VMs will be in the shutdown state.
None of those VMs will be restarted by Phagescan.
And none of those VMs will be automatically removed.
The solution is to manually remove all of them and tell Phagescan to start up new VMs.

If you experience a forced poweroff, here is what you should do upon rebooting:

0. Log into the Phagescan server status page and click the "X" icon next to one engine from each VM type to destroy
   the workers. (i.e. clicking the 'X' for Panda, Symantec, and Kaspersky will destroy all of the 3 types of VMs,
   because they each run on a different VM type).
1. Log into the OpenStack interface, go to the "Instances" page, and Force Destroy any instances in the "shutdown" state.
2. Properly reboot the master box::

    $sudo shutdown -r now

3. Upon reboot, log into the Phagescan server status page and click the Up arrow next to one engine from each VM type
   to start up the workers. (i.e. clicking the up arrow for Panda, Symantec, and Kaspersky will start up the 3 types
   of VMs, because they each run on a different VM type).

Scanners Are Failing
====================

There are a number of reasons why this could happen.
The most common reasons are:

* One or more of the worker VMs is out of disk space.
* Celery tasks are not functioning properly.

If the worker VM is out of disk space, the easiest thing to do is to destroy that worker VM type and re-create it.

If the Celery tasks are not functioning properly, the easiest thing to do is to
Stop all Scan Master Celery and Django services and the RabbitMQ application and then restart them.

See restart under :doc:`Starting/Stopping All Django and Celery Services </topics/master/index>`.


Error Messages
==============

PAGE UNAVAILABLE DUE TO SERVER HICCUP
-------------------------------------

On the Phagescan UI status page, I get error: "PAGE UNAVAILABLE DUE TO SERVER HICCUP", what does that mean?

There are several reasons for this but they fall into 2 categories.
1. You tried to start/stop a set of VM's and OpenStack returned an error.
2. The Celery Queues are in a bad state.

For the first category, you can just wait a moment and reload the page.
Then you'll get the page you want.
But you'll still need to investigate why OpenStack returned an error.
The logs in /var/log/ are a good place to start.
You can also look at the OpenStack UI under Instances, to see if there are shutdown VM's or it is out of resources.

Be patient when starting VM's. It can take up to 15 minutes to fully start a new batch of VM's.

For the second category, you can usually just restart the master services.
See :doc:`Starting/Stopping All Django and Celery Services </topics/master/index>`.

