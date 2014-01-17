=====================
Phagescan Development
=====================

To develop on Phagescan, first go through the :doc:`Quick Installation </topics/installation/index>` to get a `phagedev` VM setup.
If you do not want to use VM's, we have :doc:`Manual Instructions </topics/installation/dev/manual>`, so you can do everything on your development host.

There are some important facts about these vagrant VMs to note:

1. The [Project_root_dir] directory on your development host will be mapped
   read/write into the vagrant VM as /vagrant. So you can use an editor/IDE
   on files on your development host and execute your code/tests inside your vagrant VM.
2. When you ssh into the vagrant vm, you will be user 'vagrant' which has
   no password and has sudo privileges.
3. The python virtualenv on each vagrant vm is in /opt/psvirtualenv.
4. The Vagrantfile is in [Project_root_dir].
5. Once your VM is fully built, it is a good idea to halt it and
   take a snapshot. Then you can quickly revert to a clean VM should you
   experience problems during development.
6. Port 8000 in the vagrant VM can be accessed by localhost:8090 on your development host.

Prepare your Environment
========================

Setup Git
---------

Make sure your have git fully setup on your development host::

    $ git config --global user.name "yourUserName"
    $ git config --global user.email you@domain.com

Fork our GitHub repo in your own GitHub account.
If you haven't already, clone your forked repo::

    $ git clone git@github.com:<YOUR GITHUB USER>/phagescan.git
    $ cd [Project_root_dir]
    $ git remote add upstream git@github.com:scsich/phagescan.git

If you already cloned the repo, update your Git remotes::

    $ cd [Project_root_dir]
    $ git remote rm origin
    $ git remote add upstream git@github.com:scsich/phagescan.git
    $ git remote add origin git@github.com:<YOUR GITHUB USER>/phagescan.git

Refresh your repo and select your git branch::

    $ git pull
    $ git branch --all
    $ git checkout -b <mybranch> origin/<mybranch>

For your Python SDK, you have the choice of working with an SDK that is located within a Vagrant VM, or working with
an SDK that is local to you development host. The following two sections walk you through those options.

Remote Python SDK in VirtualEnv in a Vagrant VM
-----------------------------------------------

.. _`PyCharm`: http://www.jetbrains.com/pycharm/

If you use the SDK in a Vagrant VM, it will be fully setup by the automated Salt provisioner when you start the VM.
As such, the only thing else you need to do is configure your IDE to use it.

We recommend that you use `PyCharm`_ as your Python IDE.
It is able to use the SDK located within a Vagrant VM and execute code and tests within that Vagrant VM.
This leaves your development host free of extra python libs and other tools.
Use the :doc:`PyCharm Guide </topics/development/pycharm_vagrant>` to create a new Python Project and connect it with your Vagrant VM.


Local Python SDK in VirtualEnv on development host
--------------------------------------------------

If you do not want to use the SDK in a Vagrant VM and instead wish to use one local to your development host,
this section will help you install everything in a Python Virtual Environment.

We still recommend `PyCharm`_, because it is one of the best Python development IDE's around.

Install necessary OS packages::

    If running Ubuntu:
    $ sudo apt-get install $(< [Project_root_dir]/PACKAGES.ubuntu)
    $ sudo apt-get install $(< [Project_root_dir]/installation/scanmaster/PACKAGES.ubuntu)

Build & activate a virtual environment::

    $ virtualenv --setuptools ~/psvirtualenv
    $ source ~/psvirtualenv/bin/activate

Your prompt should look like this after::

    (psvirtualenv)[user@host]$

If you need to deactivate the virtual env (don't do this now)::

    (psvirtualenv)[user@host]$ deactivate

Install Python requirements into Virtualenv::

    (psvirtualenv)[user@host]$ pip install -r [Project_root_dir]/installation/dev/PACKAGES.pip
    (psvirtualenv)[user@host]$ pip install -r [Project_root_dir]/installation/scanmaster/PACKAGES.pip
    (psvirtualenv)[user@host]$ pip install -r [Project_root_dir]/installation/scanworker/PACKAGES.pip


Now you can start development. There are some handy scripts and config files in [Project_root_dir]/dev/.

Remember that on the VM you have to manually start/stop celery and django.

The simplest thing to do is to run everything as the user 'vagrant', which is the user you are logged in as when
you connect to a Vagrant VM using ssh.

Creating new Engines
====================

All you are doing when creating an engine is creating a Python wrapper around a tool that you want to run.
There are two types of engines:

1. Metadata engines - returns data about files, but does not make a good/bad judgement.
2. Evilness engines - makes a good/bad judgement, but has the option to return other data as well.

TODO.. add more..