.. this file replaces salt-production/README

==================================
Using Salt to Build Production VMs
==================================

TODO....

This document describes how to use salt and the states in salt-masterless/salt
for your production environment.

The files in this directory are intended to be used by the production salt master.

Perform the following steps.


0. Clone this full repo (phagescan) to a user directory on your salt master host.
The actual location doesn't matter.

----

1. Edit autosign.conf

Ensure the pattern matches what your scan workers hostnames will be.
Ensure salt-masterless/salt/top.sls has an entry matching that pattern.

Copy autosign.conf to /etc/salt/

----

2. Edit master config

You should edit 'master' to enter your correct file_roots, pillar_roots, and git_remotes.
They are further explained in the following steps.

When you are done editing, copy master to /etc/salt/master on your salt master host.

----

3. Place install media

# GIT
While it would work, it is not recommended to use a git repo for large files.
So, we are going to assume that your media will not be in a git repo.

# Manual
Assuming you use the default media location of /srv/media, copy all of your install media
to /srv/media on your salt master host. Also, ensure the master config has an entry
under file_roots for /srv/media under the 'media' environment.

file_roots:
  media:
    - /srv/media

The required directory structure in /srv/media must be like the following:

/srv/media/<salt state name>/<media files for that state>

An example salt state of salt-masterless/salt/avira/ would have media files as follows:

/srv/media/avira/installer.deb

NOTE: Ensure you place the scanmaster and scanworker .zip archives into your media directory.
They can be created by running the following scripts:

installation/scanmaster/make_scanmaster_zip.sh
installation/scanworker/make_scanworker_zip.sh

Note: Be sure to set your desired git branch in those scripts before running them.

----

4. Place licenses

# GIT
If you use git for your licenses, you do not need to place the license files manually.
Simply update your git repo details in the master config under gitfs_remotes to include
your licenses repo. It looks like the following:

gitfs_remotes:
  - git+ssh://git@github.com/myuser/phagescan-licenses.git

Note: your git repo must have a single branch in it that is named 'lic'.
If you have a 'master' branch, rename it to 'lic'.

# Manual
If you are not using git for your licenses, you must include an entry in the master
config under file_roots. Use the 'lic' environment and include the path where your
licenses are stored. Ensure there is no licenses entry under gitfs_remotes.

For consistency, store the license data in /srv/licenses

file_roots:
  lic:
    - /srv/licenses

The required directory structure in /srv/licenses should be the same as that for the media.

----

5. Place pillar and update values

# GIT
It is possible to keep pillar in a git repo, but we will assume that you will not do so.

# Manual
Copy the salt-masterless/pillar directory to /srv/pillar.

Edit /srv/pillar/settings.sls to set production values for ps_root, usernames, passwords,
licenses, etc.

Ensure the pillar_roots settings in the master config matches your directory name and
uses the 'base' environment.

pillar_roots:
  base:
    - /srv/pillar

----

6. Place salt states

# GIT
If you use git for your salt states and have an entry in the master config under
gitfs_remotes with your phagescan git repo, you do not need to place the salt states
manually. Remember to include the gitfs_root settings in the master config when you
have phagescan as a gitfs_remotes entry.

gitfs_remotes:
  - git+ssh://git@github.com/myuser/phagescan.git

gitfs_root: installation/salt-masterless/salt

If you use git for your salt states, the salt master will have access to updated states
immediately when you push them to the remote repo.

Note: salt will use the 'master' branch as its base environment, so put your latest code
in that branch. Do NOT include branches named 'lic' or 'media' in this repo. It will
conflict with your media and licenses environments.

# Manual
If you wish to manually place your salt states, ensure there is no gitfs_remotes entry
for phagescan git repo and no gitfs_root setting in the master config. Then clone the
phagescan git repo to /srv/phagescan. Then in the master config add a file_roots entry for
 it under the 'base' environment.

file_roots:
  base:
    - /srv/phagescan/installation/salt-masterless/salt

With the manual method, you'll have to manually do a git pull in /srv/phagescan to update
your salt states when there are any changes.

----

7. Restart salt-master service

Once you restart the salt-master service, you can start using salt to build scanworkers.

At this point the phagescan repo that you cloned to your user directory in step 0
is no longer needed.
