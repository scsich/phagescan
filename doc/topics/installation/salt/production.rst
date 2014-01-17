.. this file replaces salt-production/README

.. _`Salt`: http://docs.saltstack.com/
.. _`Salt Install`: http://docs.saltstack.com/topics/installation/index.html

=====================================
Build Production Worker VMs with Salt
=====================================

This document describes how to use Salt and the states in salt-masterless/salt
to build VMs for your production environment.

In order to use Salt to build production VMs, you need to first build a Salt Master.
These instructions will have you first build a Salt Master VM, and then
we will use the Salt Master to automatically build Production Scan Worker VMs.

To build Productions VMs, you need a `Salt`_ Master.
You can build a Salt Master Manually or with Vagrant.
The following instructions walk you through both options.

Build a Salt Master VM with Vagrant
===================================

Before starting these instructions:
1. You must have a working Phagescan Scan Master setup.
2. You must have created the Salt support directories and populated them with any install-media, licenses, and pillar configs.

This is the less secure option, but is faster.
It is less secure because it uses the Salt states and support files via a file share mounted at /vagrant.
That file share is the [Project_root_dir] from the Scan Master.

On the scan master, you will note the production Salt configuration files in::

    [Project_root_dir]/installation/salt-production/

The files in this directory are intended to be used by the production Salt master and production Scan Workers.

You'll also note the Vagrant file in::

    [Project_root_dir]/Vagrantfile

It has definitions for VMs that start with `prod_`.
You'll notice that they are defined to use the `minion` file from `salt-production` instead of the one from `salt-masterless`.
The production minion file defines the Salt Master's IP Address, which
by default it is the IP address of the `salt` VM that is also defined in the Vagrantfile.

So, we need to first build the `salt` VM with Vagrant, then we can use Vagrant to spin up ``prod_<os>`` VMs.

Perform the following steps on the Phagescan Scan Master.

Start up the ``saltmaster`` VM with Vagrant::

    $ cd phagescan
    $ vagrant up saltmaster

Once the Salt Master is up and running, ssh onto it::

    $ vagrant ssh saltmaster

Copy autosign.conf to Salt's config directory::

    $ sudo cp installation/salt-production/autosign.conf /etc/salt/

Edit /etc/autosign.conf as necessary. Ensure the host patterns match what your scan worker's hostnames will be.
If you are using the Vagrant-created VM's, the defaults will work for you.

Copy the Salt master config to Salt's config directory::

    $ sudo cp installation/salt-production/master /etc/salt/

* If you created the Salt support directories on the Scan Master in a location other than the defaults, you'll have to
  update the Salt Master config with those paths. By default the Salt Master config looks for all of the support directories
  under /vagrant, which translates to the Scan Master's phagescan/ directory.

Restart the Salt Master service::

    $ sudo service salt-master restart



Build a Salt Master VM Manually
===============================

This is the more secure option, but takes longer.

These instructions assume you are using an Ubuntu host/VM as your Salt Master.
However, you can use any OS that is supported by `Salt`_.

First, install the Salt Master software.
Refer to the `Salt Install`_ docs for instructions to do that.
We generally use the bootstrap script and provide the option to only install the Salt Master.

Clone the phagescan repo to a user directory on your salt master host.
The actual location doesn't matter, because we will be moving it.

::

    $ git clone git@github.com:scsich/phagescan.git

Move the phagescan directory to /srv/::

    $ sudo mv phagescan /srv/

Copy autosign.conf to Salt's config directory::

    $ sudo cp phagescan/installation/salt-production/autosign.conf /etc/salt/

Edit /etc/autosign.conf as necessary. Ensure the host patterns match what your scan worker's hostnames will be.
If you are using the Vagrant-created VM's, the defaults will work for you.

* Ensure /opt/phagescan/installation/salt-masterless/salt/top.sls has an entry matching that same hostname pattern.
  The defaults match, so you should only have to change things if you change the defaults.

Now we have to create the Salt support directories. This is where the Pillar, Install Media, and Licenses will be stored.
These can be local files or git repos.
These instructions assume local files for each of those.
See :doc:`Salt Master Directories </topics/installation/salt/directories>` for more details.

We are going to use the /srv/ directory to store all of our Salt files locally on the Salt Master.
We will use /srv/phagescan/dev/vagrant_prep.py to setup our directories for us.

Go to /srv/phagescan::

    $ cd /srv/phagescan

Edit dev/vagrant_prep.py::

    $ vi dev/vagrant_prep.py

In vagrant_prep.py, make the following changes to the ``conf`` dictionary:

1. In the 'PILLAR' config, set 'DST_PATH' to /srv/pillar::

    'DST_PATH': '/srv/pillar',

2. In the 'MEDIA' config, set 'DST_PATH' to /srv/install-media::

    'DST_PATH': '/srv/install-media',

3. In the 'LICENSES' config, set 'DST_PATH' to /srv/licenses::

    'DST_PATH': '/srv/licenses',

4. In the 'WORKER' config, set 'DST_PATH' to  /srv/install-media/scan_worker::

    'DST_PATH': '/srv/install-media/scan_worker',

5. In the 'MASTER' config, set 'DST_PATH' to  /srv/install-media/scan_task_master::

    'DST_PATH': '/srv/install-media/scan_task_master',

Now, run vagrant_prep.py to create those directories::

    $ sudo dev/vagrant_prep.py

Check your work::

    $ ls -R /srv/

* You should see the 4 directories.

Populate the licenses and install-media directories and update the settings in pillar/settings.sls.
For settings.sls, make sure to at least update `ps_root` and any usernames and passwords.

* Note: ps_root is the Phagescan root as it will exist on other Worker VMs, not the Salt Master.
* Refer to the :doc:`Salt Master Directories </topics/installation/salt/directories>` docs for guidance.

Update the Salt master config ``/etc/salt/master``.
Most importantly, you should update the variables: file_roots, pillar_roots, and git_remotes to ensure
they match your directory structure.

The following shows what those variables will look like if you use the defaults provided above::

    file_roots:
      base:
        - /srv/phagescan/installation/salt-masterless/salt
      media:
        - /srv/install-media
      lic:
        - /srv/licenses

    pillar_roots:
      base:
        - /srv/pillar


    #gitfs_remotes:
    #  - git+ssh://git@github.com/myuser/phagescan.git

    #gitfs_root: installation/salt-masterless/salt


There is no need to change the files in /srv/phagescan, so if you ever want to pull down updated versions of
those files, you can do a git pull.

Restart salt-master service::

    $ sudo service salt-master restart

Once you restart the salt-master service, you can start using salt to build scanworkers.


Build Production Scan Worker VMs
================================

