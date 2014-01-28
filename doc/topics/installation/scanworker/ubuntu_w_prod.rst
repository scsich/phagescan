=====================================
Build an Ubuntu Scan Worker with Salt
=====================================

These instructions are for building/configuring an Ubuntu scan worker host (or VM) using Salt.
This is how you would build a production scan worker.

This guide was developed against an Ubuntu 12.04 system.


Prepare your Base VM
====================

Create the base VM in any way that you desire.

* Use the "Basic Server Install" option and install all updates.
* Use the hostname ``prod.worker.ubuntu`` to take advantage of default Salt Master configuration settings.
* The vm/host **must have 2GB of RAM** or more.
  Essentially, you need to increase RAM as you increase the number of engines running on that VM.

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

* Currently, every engine is supported on an Ubuntu Worker except Symantec and Panda.
