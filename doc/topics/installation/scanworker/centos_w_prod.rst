====================================
Build a CentOS Scan Worker with Salt
====================================

These instructions are for building/configuring a CentOS scan worker host (or VM) using Salt.
This is how you would build a production scan worker.

This guide was developed against a CentOS 6 / RHEL 6 based system.
CentOS 6.3 was installed with the "Minimal" option selected and then updated with ``yum update``.
CentOS 6.4 has been tested successfully as well.

Prepare your Base VM
====================

Create the base VM in any way that you desire.
* Use the "Minimal" option and install all updates with ``yum update``.
* Use the hostname ``prod.worker.centos`` to take advantage of default Salt Master configuration settings.
* The vm/host **must have 4GB of RAM** or more, else your later step to install the Symantec engine will fail!

Install the Salt Minion client ``salt-minion`` onto your VM.
Refer to `Salt Install`_ documentation for reference.

Edit the ``/etc/salt/minion/`` file and define the ``master`` variable as the IP address of the Salt Master VM.
Then restart the ``salt-minion`` service::

    $ sudo service salt-minion restart

At this point, the base VM is ready for the Salt Master to install and configure it as a Scan Worker.

.. _`Salt Install`: http://docs.saltstack.com/topics/installation/index.html

Install Scan Worker States
==========================

The Salt states are setup to create a Scan Worker with celery automatically started on boot.
You only have to run this one command on the VM and Salt will do the build for you::

    $ sudo salt-call state.highstate

The output of this command will be colored Green/Red/Teal. If you see any Red, then you have a problem that you'll have
to investigate and resolve. If you only see Green/Teal, your VM should be ready to go.

Install chosen engines
======================

Refer to the following files::

  [Project_root_dir]/engines/[engine_name]/INSTALL

* Currently, only the Symantec engine is supported on CentOS

