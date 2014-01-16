.. this file replaces /installation/dev/INSTALL.vagrant-salt
.. TODO: merge the content from /installation/dev/README.vagrant-multiple-vms into this doc as well.

Build development VMs with Vagrant and Salt
===========================================

The following instructions will build development VM(s) using vagrant
and salt. You can ignore the base INSTALL, scanworker INSTALL, and scanmaster
INSTALL docs.

Throughout this document, the term "development host" is the physical
host that will contain your source code and will run the vagrant VMs.
Also, [Project_root_dir] is the root directory of PhageScan

There are some important facts about these vagrant VMs to note:
a. The [Project_root_dir] directory on your development host will be mapped
   read/write into each vagrant VM as /vagrant. So you can use an editor/IDE
   on your development host and execute your code/tests inside your vagrant VM.
b. When you ssh into the vagrant vm, you will be user 'vagrant' which has
   no password and has sudo privileges.
c. These vagrant VMs should not be used for production.
d. The python virtualenv on each vagrant vm is in /opt/psvirtualenv.
e. The Vagrantfile is in [Project_root_dir].
f. Once your VM is fully built, it is a good idea to halt it and
   take a snapshot. Then you can quickly revert to a clean VM should you
   experience problems during development.




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






5. Check the status of your vagrant install

$ vagrant status

It should output something like the following:

#EXAMPLE OUTPUT#
Current machine states:

uworker not created (virtualbox)
cworker not created (virtualbox)
phagedev not created (virtualbox)

The environment has not yet been created. Run `vagrant up` to
create the environment. If a machine is not created, only the
default provider will be shown. So if a provider is not listed,
then the machine is not created for that environment.
#/EXAMPLE OUTPUT#


6. Start up your first VM

You have 3 vm's to choose from:
cworker - CentOS 6.3 x64 PhageScan worker
uworker - Ubuntu Precise 64 PhageScan worker
phagedev - Ubuntu Precise 64 PhageScan worker and master combined

You can have at most 1 of each of the above 3 vms running at any one time.

You will run the vagrant commands on each VM by specifying the VM name:
vagrant up [ uworker | cworker | phagedev ]
vagrant ssh [ uworker | cworker | phagedev ]
vagrant halt [ uworker | cworker | phagedev ]

So, let's use the phagedev vm:

$ vagrant up phagedev

When you run vagrant up, if you have not already downloaded the box for it,
it will be downloaded automatically. Once it is downloaded, it will use
the Salt provisioner to load the respective set of base packages.

Note: If you get an error about Guest Additions Version being different
from your VirtualBox version, update them to be the same major.minor versions.


7. SSH into your vagrant host to verify build

$ vagrant ssh phagedev

Ensure that all salt states are set

$ sudo salt-call state.highstate


8. What else can you do:

8a. (Optional) Install selected engines into your vagrant VM. See:

[Project_root_dir]/installation/salt-masterless/salt/roots/salt/<engine>/README

8b. (Optional) Configure IntelliJ on your development host to execute tests
    and code inside your vagrant vm. See
[Project_root_dir]/installation/dev/README.vagrant-IntelliJ

8c. (Optional) Configure multiple vagrant VMs to communicate. See:
[Project_root_dir]/installation/dev/README.vagrant-multiple-vms


9. Start Development

9a. You have to manually start celery and django.

Run everything as the user 'vagrant'.
$ cd [Project_root_dir]
$ cp scanmaster/workerceleryconfig.py .
$ cp scanmaster/masterceleryconfig.py .
$ source /opt/psvirtualenv/bin/activate

For the remaining steps, refer to installation/dev/INSTALL steps 6-10.

See section 8c above if you are running the worker on a vm
other than phagedev.


9d. To connect to the django instance:

- From development host: http://localhost:8090
- From other vagrant vms: http://192.168.33.10:8000


