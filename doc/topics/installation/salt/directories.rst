
.. _`Salt's Documentation`: http://docs.saltstack.com/
.. _`Salt gitfs reference`: http://docs.saltstack.com/topics/tutorials/gitfs.html

======================================
Salt Directories for Dependency Files
======================================

For general Salt configuration and usage, see `Salt's Documentation`_.

In Phagescan, Salt needs 4 directories.

1. States - State files (.sls) define the configuration actions Salt will perform.
2. Pillar - Pillar files (.sls) define protected global variables (usernames, passwords, paths, etc)
3. Installation Media - Media files (.tar, .deb, .rpm) contain packages of software and files to be installed into a VM.
4. Licenses - License files are for commercial software licenses; many engines are commercial software.

The States are a part of the Phagescan repo, so there is nothing else to do.
The Phagescan repo has a pillar-sample directory that is used to create the Pillar directory.
The Installation Media and Licenses directories have to be created.

Content of Salt Directories
===========================

Salt
----

This directory stores all of the salt states and some service configuration files.
You should not have to make any changes to them.


Pillar
------

This directory stores all of the protected information and global variables that Salt uses when configuring a VM.
The Phagescan repo has a pillar-sample directory that has a default set of files, which are sufficient for
development use. That is why the `vagrant_prep.py` script simply copies `pillar-sample` to `pillar`.

Pillar-sample can be found at [Project_root_dir]/installation/salt-masterless/pillar-sample

In a production environment, the settings.sls file should be updated to change the ps_root and usernames/passwords.

The bottom portion of the file is for engines and licenses; some of which require definition of a variable a text string.
One example is the ESET update username and password.

If you want to move the Pillar directory to a different location, update the Master or Minion config file.
See `Salt's Documentation`_ for assistance.

Licenses
--------

This directory stores all of the licenses for the software that is installed by Salt.
The directory structure should be::

    licenses/<salt state  name>/<engine license file>

As an example, the license that goes with salt states in salt/avira/ would be::

    licenses/avira/hbedv.key

As an alternative, you can keep licenses in a GIT repository. To do that, create a repository
that uses SSH shared key for access. Name the repository anything you want, we'll call it `my-lic`
for this example. In the repository, you should have a `master` branch containing your licenses.
It should use the following directory structure pattern::

    my-lic/<salt state name>/<engine license file>

As an example, the license that goes with salt states in salt/avira/ would be::

    my-lic/avira/hbedv.key

Then, in salt-production/master, add your repo to the `gitfs_remotes` section. Assuming we
are also using GIT to store our salt states in a repo named `salt-states`, your gitfs_remotes
would look like this::

    gitfs_remotes:
      - git+ssh://git@github.com/myuser/salt-states.git
      - git+ssh://git@github.com/myuser/my-lic.git

The user running the salt master must have an ssh key connected with the repository.

Lastly, install the python module GitPython >= 0.3.0 and after you restart the salt-master,
the gitfs remote file sources will be active. (they are cached locally, but checked each time
a salt command is run). See the `Salt gitfs reference`_.

Installation Media
------------------

This directory stores all of the local installation media that is installed by Salt.
The directory structure should be::

    install-media/<salt state  name>/<engine files>

As an example, the media that goes with the states in salt/avira/ would be::

    install-media/avira/antivir-server-prof.tar.gz

As with Licenses, the install-media files can be backed up by a git repo, but realize the repo will be several GB, so
it may not be the best idea.

Define Location of Salt Directories
===================================

The Salt `master` and `minion` configuration files are preconfigured to with a default location for each of these directories.
Those files can be found in two locations.

1. For a masterless minion, the minion config is: `[Project_root_dir]/installation/salt-masterless/salt/minion`.
2. For a mastered minion, the master and minion configs are: `[Project_root_dir]/installation/salt-production/[master | minion]`.

The default location for each of the Salt directories is as follows:

1. States are in [Project_root_dir]/installation/salt-masterless/salt
2. Pillar are in [Project_root_dir]/installation/salt-masterless/pillar
3. Installation Media are in [Project_root_dir]/installation/install-media
4. Licenses are in [Project_root_dir]/installation/licenses

The script, `[Project_root_dir]/dev/vagrant_prep.py`, is used to automatically create these directories for you.
It has some variables at the top that allow you to create these Salt directories from other existing sources.
See the `PILLAR`, `MEDIA`, and `LICENSES` variables in the `conf` dictionary at the top of `vagrant_prep.py`.

Creating Salt Directories
=========================

Automatic Creation
------------------

The fastest way to create the Salt directories is to use `[Project_root_dir]/dev/vagrant_prep.py`.
By default, it will copy pillar-sample to pillar, create an empty license directory, and create an install-media directory
containing the scan_task_master and scan_worker source code .zip files.
If you want anything else, see the `PILLAR`, `MEDIA`, and `LICENSES` variables in the `conf` dictionary at the top of `vagrant_prep.py`.

Manual Creation
---------------

To do it manually, do the following:

1. installation/salt-masterless/pillar

  Copy pillar-sample to pillar. Update settings.sls and top.sls files with your values.

2. installation/install-media/{scan_task_master, scan_worker}

  Create the directory installation/install-media. In there you should place your installation
  media in separate sub-directories. Most importantly, you MUST create the two sub-directories
  `scan_task_master` and `scan_worker`.
  Run installation/scanmaster/make_scanmaster_zip.sh and place the .zip into `scan_task_master`.
  Run installation/scanworker/make_scanworker_zip.sh and place the .zip into `scan_worker`.

3. installation/licenses

  In there you should place your commercial licenses in separate sub-directories.

Note: For the install-media and licenses directories, the sub-directories should be named
similarly to the names of the salt states that are using those files. Refer to the salt
states that you intend to use for the proper naming of your license and install-media
sub-directories and files. For example, salt states in::

    installation/salt-masterless/salt/avast/

Would have install-media and licenses in::

    installation/install-media/avast/
    installation/licenses/avast/

