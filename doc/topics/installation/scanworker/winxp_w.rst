===================================
Manually Build a WinXP Scan Worker
===================================

These instructions are for manually building/configuring a Window XP scan worker host (or VM).
We do not currently support building Windows XP scan workers using Vagrant/Salt, so this is the only method.
This is how you would manually build a production scan worker. It is only lacking the automated startup scripts
for celery.

If you are building a production scan worker, you should create a user specifically to run Phagescan and then run everything
as that user.
We use the user `avuser` by default.

Prepare your Environment
========================

On the scan master, create scan_worker.zip by using the script::

    installation/scanworker/make_scanworker_zip.sh

Transfer scan_worker.zip to the Windows XP host.

* Note: One way to easily transfer files to the WinXP vm is to use a rudimentary webserver on the VM Host.
  On the VM Host, run this command in the directory containing files that need to be transferred onto the XP VM::

    $ python -m SimpleHTTPServer 7878

  Then in the XP VM, you can use the web browser to go to the IP of the VM Host on port 7878::

    http://192.168.33.10:7878/scan_worker.zip

Extract ``scan_worker.zip`` to ``c:\`` to create ``c:\phagescan``.
We will refer to this directory as [Project_root_dir]

Install python 2.7.x, setuptools, pip and virtualenv

Follow these instructions:
http://docs.python-guide.org/en/latest/starting/install/win/

* Make sure you get the latest version of python in the 2.7.x series.
  Get the python x86 msi installer.
  Install for all users and accept all defaults.

* Once you install python and update your PATH, then setuptools and pip will install.
  Just download the .py files and double-click them (setuptools first, then pip).

* To install Virtualenv, use the windows command terminal to run pip.

Start a cmd terminal, create a virtual environment, and activate it::

    $ virtualenv c:\psvirtualenv
    $ c:\psvirtualenv\Scripts\activate

Your prompt should look like this after::

    (psvirtualenv) C:\<path> >

If you need to deactivate the virtual env::

    $ deactivate

If all of the above worked, close that terminal window.

Install & Setup MinGW:

* Some requisite python packages must be compiled.  We will utilize MinGW to compile these packages on Windows.
  Follow the Graphical User Interface Installer instructions here:
  http://www.mingw.org/wiki/Getting_Started

* Select the following packages for installation::

    mingw-developer-tools, mingw32-base,  mingw32-gcc-g++, msys-base

* Once the installation is complete, refer to the "After Installing You Should ..." section on
  the Getting_Started page. Follow the instructions to create the fstab file for MSYS.

* Then move to the "Environment Settings" section and add MinGW and MSYS to your system PATH::

    Add ";C:\MinGW\bin;C:\MinGW\MSYS\1.0\bin;C:\MinGW\MSYS\1.0\local\bin;" to the system PATH.

* Lastly, instruct Python to utilize MingW as the compiler.

    1. Open (or create) ``c:\psvirtualenv\Lib\disutils\distutils.cfg``
    2. Write the following into that file::

        [build]
        compiler=mingw32

For the remainder of this document, you should open a new cmd window
and activate the virtual environment. You should be in the [Project_root_dir]
directory.

Install necessary Python packages::

    (psvirtualenv) $ pip install -r installation\scanworker\PACKAGES.pip

* For testing you can also install these::

    (psvirtualenv) $ pip install -r installation\dev\PACKAGES.pip

Copy the appropriate celery config file to the Project_root_dir::

    (psvirtualenv) $ copy installation\scanworker\workerceleryconfig.py workerceleryconfig.py

Edit workerceleryconfig.py as necessary.  In particular, tailor BROKER_CONF to your environment.

Install chosen engines
======================

Refer to the following files::

  [Project_root_dir]/engines/[engine_name]/INSTALL

* Only the Panda engine is currently supported on Windows XP

Start the Celery worker process
===============================

Use the following command to manually start celeryd::

    (psvirtualenv) $ celeryd -l INFO -E --config=workerceleryconfig -P solo

----

Running celeryd at boot
-----------------------

You can use a scheduled task to run the batch file celeryd.winxp.bat at boot.

Get batch file from the scan master.
It is in: installation/salt-masterless/salt/celery/worker/celeryd.winxp.bat.

Copy the batch file to [Project_root_dir].

Schedule a task to run this script at boot using the following steps:

1. First, you have to change the user to have a password and login to require a password::

    Start -> Control Panel -> User Accounts
    Click on your user
    Click on 'Create a password'
    Set a password.
    Make your files private.
    Click Apply, then Ok.


2. Next, create the task::

    Start -> All Programs -> Accessories -> System Tools -> Scheduled Tasks
    Double-click Add Scheduled Task
    Click Next
    Browse to find celeryd.winxp.bat
    Select 'When my computer starts'
    Specify the user/password to run the task.
    - Start it as the user 'HOSTNAME\avuser'.
    - Enter the password for user 'avuser'.
    Click the box to open the Advanced Properties
    Click Finish
    - If you get an error about Access denied, click Ok.
     Then when the Advanced Properties window appears,
     click the Set password.. button to re-enter the password for avuser.
    In the Advanced Properties, go to the Settings tab and uncheck all boxes.
    Click Apply
    Click Ok

It is possible to create a proper window service to start celery at boot, but we have yet to do so.
It would probably involve the use of pywin32.