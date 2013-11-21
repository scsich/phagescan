#!/bin/bash
#
# This script will update the signatures for a set of AV engines.
#
#  av_sig_updater.sh [<engine1> <engine2> ... ]
#
# When no engines are provided as arguments, it uses the engines
# defined by the av_engines variable.
#
# 
# When adding additional engines:
# 1. Add the function that will update the engine as update_engine(),
#    where 'engine' is the lowercase name of the AV engine.
# 2. Add the lowercase engine name to the av_engines list.
# 3. The update_engine() function must be defined above 
#    the for loop at the bottom.
#
#

# avast, avira, clamav, eset, kaspersky, sophos, [symantec]
av_engines="avast avira clamav eset kaspersky sophos symantec"
UNZIP=/usr/bin/unzip
WGET=/usr/bin/wget
CURL=/usr/bin/curl
SOPHOS_IDES_FILE=493_ides.zip
TEMP_DIR=/tmp

# Check for optional list of engines as input arg
test $# -gt 0 && av_engines="$@"
test $# -eq 1 && test "$1" = "--help" && echo " 
  $0 [<engine1> <engine2> ... ] 
  $0 --help
  " && exit 1


update_avast()
{
  UPDATER=/usr/bin/avastvpsupdate.sh
  # test for updater being installed
  test ! -x "$UPDATER" && echo 'ERROR: Update for Avast requested, but it is not installed.' && return 1

  echo 'Updating Avast signatures'
  $UPDATER
  #echo $UPDATER

  return 0
}

update_avira()
{
  UPDATER=/usr/lib/AntiVir/guard/avupdate-guard
  # test for updater being installed
  test ! -x "$UPDATER" && echo 'ERROR: Update for Avira requested, but it is not installed.' && return 1

  echo 'Updating Avira signatures'
  $UPDATER
  #echo $UPDATER

  return 0
}



update_clamav()
{
  UPDATER=/usr/bin/freshclam
  # test for updater being installed
  # run update commands
  test ! -x "$UPDATER" && echo 'ERROR: Update for ClamAV requested, but it is not installed.' && return 1

  echo 'Updating ClamAV signatures'
  $UPDATER
  #echo $UPDATER
  echo 'Restarting clamd'
  service clamav-daemon restart

  return 0
}

update_eset()
{
  UPDATER=/opt/eset/esets/sbin/esets_update
  # test for updater being installed
  test ! -x "$UPDATER" && echo 'ERROR: Update for ESET requested, but it is not installed.' && return 1

  # ensure eset has its config files and directorys created:
  /opt/eset/esets/sbin/esets_scan --clean-mode=none --no-quarantine /etc/opt/eset/esets/esets.cfg

  echo 'Updating ESET signatures'
  $UPDATER
  #echo $UPDATER

  return 0
}

update_kaspersky()
{
  UPDATER=/opt/kaspersky/kes4lwks/bin/kes4lwks-control
  # test for updater being installed
  test ! -x "$UPDATER" && echo 'ERROR: Update for Kaspersky requested, but it is not installed.' && return 1

  echo 'Updating Kaspersky signatures'
  $UPDATER --set-settings Update -N CommonSettings.SourceType=KLServers
  $UPDATER --start-task Update -N -F /tmp/kes4lwks-update-out.txt
  $UPDATER --progress Update -N
  $UPDATER --get-stat Update

  return 0
}

update_sophos()
{
  # test for updater being installed
  UPDATER=/usr/local/bin/sweep
  test ! -x "$UPDATER" && echo 'ERROR: Update for Sophos requested, but it is not installed.' && return 1

  # Ensure both wget and unzip are installed.
  test ! -x "$WGET" && echo "  ERROR: $WGET is missing." && return 1
  test ! -x "$UNZIP" && echo "  ERROR: $UNZIP is missing." && return 1

  echo 'Updating Sophos signatures'
  cd $TEMP_DIR
  test -f "$SOPHOS_IDES_FILE" && rm -f "$SOPHOS_IDES_FILE"

  $WGET -q http://downloads.sophos.com/downloads/ide/$SOPHOS_IDES_FILE
  test "$?" != 0 && echo '  ERROR: Download of $SOPHOS_IDES_FILE failed.' && return 1

  test ! -d /usr/local/sav && echo '  ERROR: Directory /usr/local/sav not found.' && return 1
  cd /usr/local/sav

  # Ensure .zip file is error free.
  $UNZIP -tqq $TEMP_DIR/$SOPHOS_IDES_FILE
  test "$?" != 0 && echo '  ERROR: $SOPHOS_IDES_FILE is an invalid .zip file.' && return 1

  $UNZIP -quo $TEMP_DIR/$SOPHOS_IDES_FILE

  test -f $TEMP_DIR/$SOPHOS_IDES_FILE && rm -f $TEMP_DIR/$SOPHOS_IDES_FILE

  return 0
}

update_symantec()
{
  # test for updater being installed
  UPDATER=/opt/SYMCScan/bin/definitions/AntiVirus/setup-iu.sh
  test ! -x "$UPDATER" && echo 'ERROR: Update for Symantec requested, but it is not installed.' && return 1

  # Ensure curl is installed.
  test ! -x "$CURL" && echo "  ERROR: $CURL is missing." && return 1

  echo 'Updating Symantec signatures'

  cd $TEMP_DIR

  # Warning: We are downloading a shell script into this dir
  # and then executing it. Be careful!

  # Note: The file we want is the latest *-unix.sh (not the -unix64.sh) 
  # The file pattern is YYYYMMDD-###-unix.sh.

  # test if connection to remote site exists
  file_list=`$CURL -s -l "ftp://ftp.symantec.com/public/english_us_canada/antivirus_definitions/norton_antivirus/" | grep "\-unix.sh"`

  # curl returns 0 when it succeeds, otherwise it will return non-zero.
  test "$?" != 0 && echo "  ERROR: Symantec update URL is un-reachable." && return 1

  # select latest signature from list of available signature sets
  file_arr=($file_list)
  file_arr_len=${#file_arr[@]}
  sym_file=${file_arr[$file_arr_len-1]}

  # Download the latest defn file
  $CURL -s -S -O "ftp://ftp.symantec.com/public/english_us_canada/antivirus_definitions/norton_antivirus/$sym_file"

  # curl returns 0 when it succeeds, otherwise it will return non-zero.
  test "$?" != 0 && echo "  ERROR: Download of Symantec definition update failed." && return 1

  # Enable sig updating and create /opt/Symantec/virusdefs/incoming dir
  cd `dirname ${UPDATER}`
  ./setup-iu.sh enable
  cd $TEMP_DIR

  # Run the update script
  # The new defs will be put into $AVDEFS_UPDATE_DIR
  bash ${sym_file}

  # Delete the update script
  rm -f ${sym_file}

  # Stop the symcscan service
  service symcscan stop

  # Delete the old defs
  AVDEFS_LIVE_DIR=/opt/SYMCScan/bin/definitions/AntiVirus/VirusDefs
  AVDEFS_UPDATE_DIR=/opt/Symantec/virusdefs/incoming
  rm -f $AVDEFS_LIVE_DIR/*

  # Copy in the new defs and fix perms
  cp $AVDEFS_UPDATE_DIR/* $AVDEFS_LIVE_DIR/
  chmod 440 $AVDEFS_LIVE_DIR/*
  chown root:avdefs $AVDEFS_LIVE_DIR/*

  # Start the symcscan service
  service symcscan start

  return 0
}


# Do not quote the $av_engines variable; else it's not a list
for engine in $av_engines; do
  # Determine if the function is defined.
  declare -f "update_$engine" > /dev/null
  if [ "$?" == 0 ]; then
    #echo "update_$engine is a func."
    update_$engine
  else
    echo "ERROR: function update_$engine is NOT defined."
  fi
done

exit 0

