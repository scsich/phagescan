#!/bin/bash
#
# Use this script to stop/start all of the services that connect to celery/rabbitmq
#
# usage: sudo ./ps_services.sh [start|stop|status]
#
# Note:
# I intentionally did not add a 'restart' state because I prefer to do a stop_app and start_app
# on rabbitmq after I stop all of these services and before I restart all of these services.
# Additionally, not all of these services support a restart state, so that will require extra logic.
#
##
if [ $# -ne 1 ] ; then
  echo "usage: sudo $0 [start|stop]"
  exit 1
fi

command="$1"
if ! [[ "${command}" == start || "${command}" == stop ]] ; then
  echo "Invalid Command."
  echo "usage: sudo $0 [start|stop]"
  exit 1
fi
#echo "command:" ${command}

echo "celeryd-periodic..."
service celeryd-periodic ${command}
echo "celeryd-reesult..."
service celeryd-result ${command}
echo "celeryd-master..."
service celeryd-master ${command}
echo "supervisor..."
service supervisor ${command}
echo "gunicorn..."
service gunicorn ${command}

exit 0
