=================
Phagescan Workers
=================

The Phagescan Worker is one of a collection of VMs running in a virtualization infrastructure.
We currently support OpenStack and EC2 for cloud computing providers.
You can also run VMs in any virtualization framework like: VMWare, VirtualBox, etc.


Using the Phagescan Workers
===========================

Once the VM is built and configured, there are only a few things that you may want to do on the VM.

Start/Stop the Celery Service
-----------------------------

In a production environment, there will be a single celery service that will start automatically.
On Linux, you can start and stop the service using the standard service scripts::

    $ sudo service celeryd start

    $ sudo service celeryd stop

In a development environment, it is often easiest to start it manually in debug mode to observe the output.

Refer to the OS-based installation documentation for the specifics:

Ubuntu

* :doc:`Manual </topics/installation/scanworker/ubuntu_w>`
* :doc:`Production </topics/installation/scanworker/ubuntu_w_prod>`

CentOS

* :doc:`Manual </topics/installation/scanworker/centos_w>`
* :doc:`Production </topics/installation/scanworker/centos_w_prod>`

Windows XP

* :doc:`Manual </topics/installation/scanworker/winxp_w>`

Start/Stop Engine Services
--------------------------

Each engine will have its own start and stop script if it is run as a service.
Some engines are simple scripts that are only executed on demand.
Refer to the Engine Installation Documentation in [Project_root_dir]/engines/[engine_name]/INSTALL for assistance.

Update Engine Signatures
------------------------

Some engines are signature-based, which we refer to as Evilness engines.
On a production system, they are configured to automatically install signature updates multiple times per day.
Provided the workers are given access to the public Internet.
There is also a periodic Celery service on the Scan Master that will attempt to update signatures every 4 hours.
However, if you want to update them manually,
refer to the Engine Installation Documentation in [Project_root_dir]/engines/[engine_name]/INSTALL for assistance.

