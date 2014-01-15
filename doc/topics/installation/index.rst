.. this file replaces the root /INSTALL file

==================
Installation Types
==================

PhageScan is a very flexible framework. In its simplest form, it can be installed on a single laptop.
In its more robust form, it requires a cloud computing environment. And you can select anything in between.

There are three primary installation types for PhageScan:

1. Everything in a single VM.

  * Easiest way to test drive Phagescan.
  * Good for development; master and worker using same code base in one VM.
  * Good for Incident Response teams; it will easily run on an average laptop.
  * Only Ubuntu is currently supported as the guest OS. So, you can only use/develop engines that run on Ubuntu.
  * Lowest resource requirements.

2. A single ScanMaster VM and a small number of manually controlled ScanWorker VMs.

  * Ideal for more extensive development and testing. You can test network functionality as well as multiple ScanWorker OS's.
  * Ideal for Incident Response teams; you can run engines on multiple ScanWorker OS's.
  * Multiple VMs take more resources.

3. A single ScanMaster Host with a collection of ScanWorkers running in a Cloud Computing environment.

  * Ideal for enterprise CIRT or IR environments.
  * Currently supports Amazon EC2 and OpenStack cloud computing environments.
  * Can be fully installed in one or more on-premise devices.
  * Higher resource requirements.

Quick Installation
==================

The fastest way to get up and running is to have Vagrant build/setup the VM(s) for you.
This will work for installation type 1 and 2.
Your host OS can be any OS that runs Salt and Vagrant.
By default, Phagescan expects an Ubuntu host, but we have also used Mac OS X.

On your host, install your preferred virtualization software and Vagrant.
We use VirtualBox on Ubuntu or VMWare Fusion on Mac OS X for virtualization software.

A couple of notes for Ubuntu hosts:

1. Use the Oracle version of VirtualBox and get the latest version (>= 4.2).
  See `Ubuntu VirtualBox help <https://help.ubuntu.com/community/VirtualBox/Installation>`_.

2. Use the `Vagrant website's <http://www.vagrantup.com/>`_ version of Vagrant.
  Get the latest version of vagrant >= v1.2.x.
  While Vagrant does have some support for Windows guests, we use Windows XP, which is not supported.


Ensure your Vagrant installation has vagrant-salt, the `Salt provisioner <http://docs.vagrantup.com/v2/provisioning/salt.html>`_.
New versions of Vagrant have it by default.

::

   $ vagrant plugin list
   vagrant-salt (0.4.0)

If you don't have it, you'll have to install the Salty Vagrant plugin.

::

   $ vagrant plugin install vagrant-salt

Next download phagescan onto your host.

Clone the phagescan git repo::

  $ git clone git@github.com:scsich/phagescan.git











This is the root INSTALL file.
 If you are performing a manual build/install for either development or
production, follow the instructions listed here first and continue onto
the appropriate INSTALL.* file as directed at the bottom.

 If you are manually building a Windows scanworker, skip the remainder of
this file and go directly to:
[Project_root_dir]/installation/scanworker/INSTALL.WindowsXP

 If you are using vagrant and salt to automatically build/install/configure
your develompment VMs, skip the remainder of this file and go directly to:
[Project_root_dir]/installation/dev/INSTALL.vagrant-salt


Ubuntu instructions were tested on 12.04 x86_64, Desktop edition.
CentOS instructions were tested on 6.3 x86_64 and 6.4 x86_64.
Windows instructions were tested on Windows XP SP3.

----

0. Clone the git repo to your development host

$ git config --global user.name "yourUserName"
$ git config --global user.email you@domain.com
$ git clone git@github.com:scsich/phagescan.git

Select your git branch:

$ cd phagescan
$ git branch --all
$ git checkout -b <mybranch> origin/<mybranch>

The phagescan directory created by git will be referred to as
[Project_root_dir] throughout the documentation.

----

1. Install necessary OS packages.

If running Ubuntu:
$ sudo apt-get install $(< [Project_root_dir]/PACKAGES.ubuntu)

If running CentOS:

We only used CentOS as a scanworker. So, skip the rest of this document
and refer to the CentOS scanworker INSTALL instructions:
[Project_root_dir]/installation/scanworker/INSTALL.CentOS

----

2. Build & activate a virtual environment
$ virtualenv ~/psvirtualenv
$ source ~/psvirtualenv/bin/activate

Your prompt should look like this after:
(psvirtualenv)[user@host]$

If you need to deactivate the virtual env:
(don't do this now) $ deactivate

----

3. Continue on to the next INSTALL file as appropriate for the build you are
creating.

If creating a development environment (scanmaster, scanworker, web server,
IDE all on the same node):
[Project_root_dir]/installation/dev/INSTALL

If creating a production scanmaster node:
[Project_root_dir]/installation/scanmaster/INSTALL

If creating a production scanworker node:
[Project_root_dir]/installation/scanworker/INSTALL
