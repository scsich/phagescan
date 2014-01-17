
.. _`VirtualBox website`: https://www.virtualbox.org/wiki/Downloads
.. _`Ubuntu VirtualBox help`: https://help.ubuntu.com/community/VirtualBox/Installation
.. _`Vagrantup website`: http://www.vagrantup.com/
.. _`Salt provisioner`: http://docs.vagrantup.com/v2/provisioning/salt.html
.. _`vagrant-salt plugin`: https://github.com/saltstack/salty-vagrant

============
Installation
============

PhageScan is a very flexible framework. In its simplest form, it can be installed on a single laptop.
In its most robust form, it requires a cloud computing environment. And you can select anything in between.

Installation Types
==================

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
This will work for installation type 1 and 2, but the following instructions will perform installation type 1.
Your host OS can be any OS that runs Salt and Vagrant.
By default, Phagescan expects an Ubuntu host, but we have also used Mac OS X.

On your host, install your preferred virtualization software and Vagrant.
We use VirtualBox on Ubuntu or VMWare Fusion on Mac OS X for virtualization software.

1. Use the latest version (>= 4.2) of VirtualBox and the VM Extension Pack from Oracle downloadable from the `VirtualBox website`_.

  * The version distributed by Ubuntu is too old; see `Ubuntu VirtualBox help`_.

2. Use the latest version (>= v1.3.0) of Vagrant from the `Vagrantup website`_.

  * The version distributed by Ubuntu is too old.
  * While Vagrant does have some support for Windows guests, we use Windows XP, which is not supported.
  * Ensure your Vagrant installation has the `Salt provisioner`_.
    New versions of Vagrant (>= v1.3.0) have it by default. If you are using a 1.2.x version of Vagrant,
    you will have to install the `vagrant-salt plugin`_ to get the Salt provisioner.

Download phagescan onto your host by cloning the phagescan git repo::

  $ git clone git@github.com:scsich/phagescan.git

You should now have a *phagescan* directory. The rest of the documentation will refer to this directory as **[Project_root_dir]**.

Prepare the directories that store the files that will be installed into the Master and Minion VMs by Salt (licenses and installation media)::

  $ cd [Project_root_dir]
  $ dev/vagrant_prep.py

* vagrant_prep.py has useful defaults, but you can customize it if you wish.
  See the :doc:`Salt Directories documentation </topics/installation/salt/directories>` for further reference.

Update the VM configuration settings in [Project_root_dir]/installation/salt-masterless/pillar/settings.sls.
For a development setup, the defaults are sufficient.
For a production setup, you should update the *ps_root* variable at the top and the passwords in the *SERVERS* section.

We are about ready to start up our first VM *phagedev*.
If you are not using VirtualBox, you should edit the [Project_root_dir]/Vagrantfile and update the settings for the *phagedev* config.
Test your Vagrant config::

  $ cd [Project_root_dir]
  $ vagrant status

It should output something like the following::

    Current machine states:

    uworker not created (virtualbox)
    cworker not created (virtualbox)
    phagedev not created (virtualbox)

There will be several machines listed, but we are interested in *phagedev*.
It is an Ubuntu Precise 64 Phagescan worker and master combined

* You can have at most 1 of each of the vms running at any one time.
* You will run the vagrant commands on each VM by specifying the VM name::

   $ vagrant up [ uworker | cworker | phagedev ]
   $ vagrant ssh [ uworker | cworker | phagedev ]
   $ vagrant halt [ uworker | cworker | phagedev ]

Start up the *phagedev* vm::

  $ vagrant up phagedev

* When you run vagrant up, if you have not already downloaded the box for it,
  it will be downloaded automatically. Once it is downloaded,
  it will use the Salt provisioner to install and configure the respective set of base packages.

SSH into your vagrant host to verify build::

  $ vagrant ssh phagedev

Ensure that all salt states are set::

  [phagedev]$ sudo salt-call state.highstate

At this point, there are some important things you need to know.

1. The *phagedev* vm has all software and libraries install for the master and worker,
   but only 2 engines are installed by default: clamav and yara.
2. The [Project_root_dir] directory on your host will be mapped
   read/write into each vagrant VM as /vagrant. So you can use an editor/IDE
   on your development host and execute your code/tests inside your vagrant VM.
3. When you ssh into the vagrant vm, you will be user 'vagrant' which has
   no password and has sudo privileges.
4. These vagrant VMs should not be used for production; the privileges and file share is very open.
5. The python virtualenv on each vagrant vm is in /opt/psvirtualenv.
6. Once your VM is fully built, it is a good idea to halt it and
   take a snapshot. Then you can quickly revert to a clean VM should you
   experience problems during use/development.

Few of the Phagescan services are started by default, so that is the next step. Configuring the Master and Worker is all
done on the *phagedev* VM, so you will need at least 5 terminals logged into *phagedev*. Remember, you can
create more terminals in the VM by ssh'ing through Vagrant::

    $ vagrant ssh phagedev

For the Master, you need to configure and start Django and 3 celery workers.
We have yet to automate these steps, so you'll have to do it manually.

1. Create Django database tables, cache, and superuser.

  The first command will prompt you to create a django superuser.  Do so.
  For development, define devuser/devpass.  Give a fake e-mail addr::

    [phagedev]$ cd [Project_root_dir]
    [phagedev]$ source /opt/psvirtualenv/bin/activate
    [phagedev]$ python manage.py syncdb --settings=scaggr.settings
    [phagedev]$ python manage.py migrate --settings=scaggr.settings
    [phagedev]$ python manage.py createcachetable --settings=scaggr.settings cache

2. Copy the appropriate Celery config files to the [Project_root_dir]::

    [phagedev]$ cp installation/scanmaster/masterceleryconfig.py masterceleryconfig.py
    [phagedev]$ cp installation/scanmaster/resultsceleryconfig.py resultsceleryconfig.py
    [phagedev]$ cp installation/scanmaster/periodicceleryconfig.py periodicceleryconfig.py


3. Collect Static files::

    [phagedev]$ python manage.py collectstatic

4. Start the celery processes, each in separate terminals::

    [phagedev]$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=masterceleryconfig -E -B -l info --hostname=master.master
    [phagedev]$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=resultsceleryconfig -E -B -l info --hostname=master.results
    [phagedev]$ DJANGO_SETTINGS_MODULE=scaggr.settings celeryd --config=periodicceleryconfig -E -B -l info --hostname=master.periodic

5. Start the django development web server.

  Run django as same user that you used to start celeryd::

    [phagedev]$ python manage.py runserver -v 3 0.0.0.0:8000 --settings=scaggr.settings

For the Worker, you only need to configure and start one celery worker.
Take advantage of the salt states to automate this step::

    [phagedev]$ sudo salt-call state.sls celery.worker

Now we have the Django Web Interface listening on port 8000 in the VM, which is mapped to port 8090 on your host.
To connect to the django instance::

    From your host: http://localhost:8090
    From other vagrant vms: http://192.168.33.10:8000

Login to the Django Web User Interface with the django superuser user/password that you created.

When you are finished and want to shutdown the *phagedev* VM, do the following:

1. Shutdown celery services
2. Shutdown Django service
3. Logout of the *phagedev* VM.
4. Halt the *phagedev* VM::

    $ vagrant halt phagedev

-----

Some final notes.

1. The Master services will not start on boot by default.

   * For Django to start at boot, you'll want to install gunicorn and supervisord. You will also want a real web server in front of django, like Apache or Nginx.
   * For the 3 celery services to start at boot, you can use the *default* and *init.d* script from the worker as a template.
     See [Project_root_dir]/installation/salt-masterless/salt/celery/[master and worker]

2. The Worker celery service will start on boot.
3. If you want to add additional Worker engines, you can use Salt to add them.
   It is generally a simple salt-call command to install and start it, but remember that you need to do a few things first:

   a. Copy the installation media to the install-media directory. See the :doc:`Salt Directories documentation </topics/installation/salt/directories>` for further reference.
   b. Copy the license to the license directory. See the :doc:`Salt Directories documentation </topics/installation/salt/directories>` for further reference.
   c. Ensure all variables in settings.sls are updated for that engine. See [Project_root_dir]/installation/salt-masterless/pillar/settings.sls.
   d. Then you can install an engine like this::

       [phagedev]$ sudo salt-call state.sls <engine name>
       [phagedev]$ sudo salt-call state.sls avira

   e. You need to restart the Master and Worker celery services after adding a new engine.


Building A Single Master or Worker
==================================

Master
------

We have partially completed the Salt states to build a scan master, but for now, you should do it manually.
To manually build a scan master, the following instructions will guide you:

* :doc:`Ubuntu </topics/installation/scanmaster/ubuntu_m>`


Worker
------

ScanWorkers can be Ubuntu, CentOS, or Windows VMs. Ubuntu instructions were tested on 12.04 x86_64, Desktop edition.
CentOS instructions were tested on 6.3 x86_64 and 6.4 x86_64.
Windows instructions were tested on Windows XP SP3.

We have Salt states to automatically build Ubuntu and CentOS Workers, but Windows scanworkers require a fully manual build.
To use Salt states to automatically build Ubuntu and CentOS workers, select the `uworker` or `cworker`
VMs from Vagrant and start them up. They will build to a base Worker with no engines installed, so you'll simply have to add engines to them.

To manually build a scan worker, the following instructions will guide you:

* :doc:`Ubuntu </topics/installation/scanworker/ubuntu_w>`
* :doc:`CentOS </topics/installation/scanworker/centos_w>`
* :doc:`Windows </topics/installation/scanworker/winxp_w>`

