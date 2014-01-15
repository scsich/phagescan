.. this file replaces /installation/scanworker/INSTALL.WindowsXP

=============================
Build a Windows XP ScanWorker
=============================


Follow these instructions to build a Windows XP scanworker.

Note: These instructions refer to the project root as [Project_root_dir].
It also assumes that the single user has username 'avuser'.


0. Extract scan_worker.zip

Extract the phagescan directory in scan_worker.zip to c:\ to create c:\phagescan

Note: Easily transfer files to the WinXP vm using a webserver on the VM Host.
On the VM Host, do this in the directory containing that need to be
transferred onto the XP VM.
$ python -m SimpleHTTPServer 7878

Then in the XP VM, you can use the web browser to go to the IP of the VM Host
on port 7878
i.e. http://192.168.10.10:7878/scan_worker.zip

----

1. Install python 2.7.x, setuptools, pip and virtualenv

Follow these instructions:
http://docs.python-guide.org/en/latest/starting/install/win/

Make sure you get the latest version of python in the 2.7.x series.
Get the python x86 msi installer.
Install for all users and accept all defaults.

Once you install python and update your PATH, then setuptools and pip will install.
Just download the .py files and double-click them (setuptools first, then pip).

To install Virtualenv, use the windows command prompt to run pip.


----

2. Install a virtual environment

Use the cmd terminal

$ virtualenv c:\psvirtualenv
$ c:\psvirtualenv\Scripts\activate

Your prompt should look like this after:
(psvirtualenv) C:\<path> >

If you need to deactivate the virtual env:
$ deactivate

If all of the above worked, close that terminal window.

----

3. Install & Setup MinGW

Some requisite python packages must be compiled.  We will utilize MinGW to compile these packages on Windows.

Follow the Graphical User Interface Installer instructions here:
http://www.mingw.org/wiki/Getting_Started

Select the following packages for installation:
mingw-developer-tools, mingw32-base,  mingw32-gcc-g++, msys-base

Once the installation is complete, refer to the "After Installing You Should ..." section on
the Getting_Started page. Follow the instructions to create the fstab file for MSYS.

Then move to the "Environment Settings" section and add MinGW and MSYS to your system PATH:
Add ";C:\MinGW\bin;C:\MinGW\MSYS\1.0\bin;C:\MinGW\MSYS\1.0\local\bin;" to the system PATH.

Lastly, instruct Python to utilize MingW as the compiler:
a) Open (or create) <path_to_your_virtualenv>\Lib\disutils\distutils.cfg
b) Write the following into that file:
[build]
compiler=mingw32



----

4. Install necessary Python packages.

For the remainder of this document, you should open a new cmd window
and activate the virtual environment. You should be in the [Project_root_dir]
directory.

(psvirtualenv) $ pip install -r installation\scanworker\PACKAGES.pip

For testing you can also install these:
(psvirtualenv) $ pip install -r installation\dev\PACKAGES.pip

----

5. Ensure we have latest version of celery 3.0.x.

$ pip install --upgrade celery==3.0.24

----

6. Copy the appropriate celery config file to the Project_root_dir.

(psvirtualenv) $ copy installation\scanworker\workerceleryconfig.py workerceleryconfig.py

----

7. Edit workerceleryconfig.py as necessary.  In particular, tailor BROKER_CONF to your environment.

----

8. Install chosen engines.

Refer to the following files:
[Project_root_dir]\engines\[engine_name]\INSTALL

----

9. Start a worker

To start a celery scan worker from the root project directory:
$ celeryd -l DEBUG -E --config=workerceleryconfig -P solo


----

10, Running celeryd at boot

Use a scheduled task to run the batch file celeryd.winxp.bat at boot.

Get batch file from installation/salt-masterless/salt/celery/worker/celeryd.winxp.bat.

  Copy the batch file to [Project_root_dir].

Schedule a task to run this script at boot

  First, you have to change the user to have a password and login to require a password.

  Start -> Control Panel -> User Accounts
  Click on your user
  Click on 'Create a password'
  Set a password.
  Make your files private.
  Click Apply, then Ok.


  Next, create the task.

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

11. Creating a proper window service to start celery at boot (optional)

Download the latest pywin32 version for python 2.7 matching your architecture:
http://sourceforge.net/projects/pywin32/files/pywin32/
