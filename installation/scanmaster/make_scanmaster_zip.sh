#!/bin/bash
##
# This script will create a zip archive named scan-master.zip in the root of the project.
# The archive will only contain only files needed by a scan master.
# It uses the master git branch by default.
#
# Run this script from installation/scanmaster/:
# $ ./make_scanmaster_zip.sh
#
##
ZIPFILENAME=scan_master.zip
GITBRANCH=`git branch | sed -n '/\* /s///p'`

# cd to root of project
cd ../../

# print name of git branch being used
echo "Creating archive of PhageScan using git branch '${GITBRANCH}'..."

# create zip file
git archive --prefix=phagescan/ -o ${ZIPFILENAME} ${GITBRANCH}^ \
AUTHORS \
COPYING \
INSTALL \
LICENSE \
PACKAGES.* \
TESTING \
manage.py \
accounts/* \
api/* \
engines/* \
installation/scanmaster/* \
monitor/* \
nsrl/* \
sample/* \
scaggr/* \
scanworker/* \
templates/* \
virusscan/* \
workermgmt/*

# print name of file and location
CWD=`pwd`
echo "Archive '${ZIPFILENAME}' created in '${CWD}'."
