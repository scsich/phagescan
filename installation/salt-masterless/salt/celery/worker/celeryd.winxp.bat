@echo off
goto :StartOfCode

================================================================================
This batch file will start celeryd within the Project_root_dir.

Usage:
  c:\phagescan\celeryd.winxp.bat

Notes:
    Use a scheduled task to run this file at boot.

    Get batch file from installation/salt-masterless/salt/celery/worker/celeryd.winxp.bat.

      Copy the batch file to Project_root_dir.

    Schedule a task to run this script at boot

      Start -> All Programs -> Accessories -> System Tools -> Scheduled Tasks

      Double-click Add Scheduled Task
      Click Next
      Browse to find celeryd.winxp.bat
      Select 'When my computer starts'
      Specify the user/password to run the task.
       - Start it as the user 'HOSTNAME\avuser'.
       - If avuser doesn't have a password set, leave password blank.
      Click the box to open the Advanced Properties
      Click Finish
       - If you get an error about Access denied, click Ok.
         Then when the Advanced Properties window appears,
         click the Set password.. button to set a password for avuser.
      In the Advanced Properties, go to the Settings tab and uncheck all boxes.
      Click Apply
      Click Ok
      Double-click on the task to test it.

================================================================================

:StartOfCode

REM Set varibles
set PROJECT_ROOT=c:\phagescan
set LOG_DIR=logs
set PYTHON=c:\psvirtualenv\Scripts\python.exe

REM Set IP Addy
set IP_ADDR=
for /f "delims=" %%f in ('ipconfig /all ^| grep "IP Address" ^| awk "{print $15}" ') do (
  @set IP_ADDR=%%f
  goto :done
  )
:done

REM Start up celeryd
cd %PROJECT_ROOT%
if not exist %LOG_DIR% mkdir %LOG_DIR%

%PYTHON% -m celery.bin.celeryd -l DEBUG -E --config=workerceleryconfig -P solo -f %LOG_DIR%\celeryd.log -n celery.%IP_ADDR%