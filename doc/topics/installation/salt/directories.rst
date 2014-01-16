.. this file replaces /installation/README and /installation/salt-masterless/README

.. talk about which directories are needed.
.. talk about where to put those dirs
.. talk about how to make them automatically/manually

======================================
Salt Directories for Dependency Files
======================================

These are the directories that will contain licenses and installation media for engine software.
Salt will expect the dependency files in these locations.

.. need to merge the following content.


.. content from /installation/README

## Licenses in local file system ##
This directory stores all of the licenses for the software that is installed by Salt.

The directory structure should be:

licenses/<salt state  name>/<engine license file>

As an example, the license that goes with salt states in salt/avira/ would be:

licenses/avira/hbedv.key

## Licenses in GIT repository ##
As an alternative, you can keep licenses in a GIT repository. To do that, create a repository
 that uses SSH shared key for access. Name the repository anything you want, we'll call it 'my-lic'
 for this example. In the repository, you should have a 'master' branch containing your licenses.
 It should use the following directory structure pattern:

my-lic/<salt state name>/<engine license file>

As an example, the license that goes with salt states in salt/avira/ would be:

my-lic/avira/hbedv.key

Then, in salt-production/master, add your repo to the 'gitfs_remotes' section. Assuming we
are also using GIT to store our salt states in a repo named 'salt-states', your gitfs_remotes
would look like this:

gitfs_remotes:
  - git+ssh://git@github.com/myuser/salt-states.git
  - git+ssh://git@github.com/myuser/my-lic.git

The user running the salt master must have an ssh key connected with the repository.

Lastly, install the python module GitPython >= 0.3.0 and after you restart the salt-master,
the gitfs remote file sources will be active. (they are cached locally, but checked each time
a salt command is run)

Salt gitfs reference: http://docs.saltstack.com/topics/tutorials/gitfs.html


This directory stores all of the local installation media that is installed by Salt.

The directory structure should be:

install-media/<salt state  name>/<engine files>

As an example, the media that goes with the states in salt/avira/ would be:

install-media/avira/antivir-server-prof.tar.gz


.. content from /installation/salt-masterless/README

You need to create 3 directories to enable the salt states to function in a masterless
environment (not production).

To do it automatically, see PROJECT_ROOT/dev/vagrant_prep.py

To do it manually, do the following:
1. installation/salt-masterless/pillar
Copy pillar-sample as a template. Update settings.sls and top.sls files with your values.

2. installation/install-media/{scan_task_master, scan_worker}
Create the directory installation/install-media. In there you should place your installation
media in separate sub-directories. Most importantly, you MUST create the two sub-directories
'scan_task_master' and 'scan_worker'.
Run installation/scanmaster/make_scanmaster_zip.sh and place the .zip into 'scan_task_master'.
Run installation/scanworker/make_scanworker_zip.sh and place the .zip into 'scan_worker'.

3. installation/licenses
In there you should place your commercial licenses in separate sub-directories.

Note: For the install-media and licenses directories, the sub-directories should be named
similarly to the names of the salt states that are using those files. Refer to the salt
states that you intend to use for the proper naming of your license and install-media
sub-directories and files.

i.e.
salt states in
installation/salt-masterless/salt/avast/

would have install-media and licenses in:
installation/install-media/avast/
installation/licenses/avast/

