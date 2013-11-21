#!/bin/bash
##
# This script will create a zip archive named scan-worker.zip in the root of the project.
# The archive will only contain the files needed by a scan worker.
# It uses the master git branch by default.
#
# Run this script from installation/scanworker/:
# $ ./make_scanworker_zip.sh
#
##
ZIPFILENAME=scan_worker.zip
GITBRANCH=`git branch | sed -n '/\* /s///p'`

# cd to root of project
cd ../../

# print name of git branch being used
echo "Creating archive of PhageScan using git branch '${GITBRANCH}'..."

# create zip archive
git archive --prefix=phagescan/ -o ${ZIPFILENAME} ${GITBRANCH} \
AUTHORS \
COPYING \
INSTALL \
LICENSE \
PACKAGES.* \
TESTING \
engines/* \
scanworker/* \
installation/scanworker/*

# print name of file and location
CWD=`pwd`
echo "Archive '${ZIPFILENAME}' created in '${CWD}'."
