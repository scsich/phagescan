#!/bin/bash

# reset the DB -- TODO: make this relative
/bin/bash dev/dev_reset_db.sh

# clean uploaded and generated files
rm -rf ./artifacts
rm -rf ./imageout
rm -rf ./samples
rm -rf ./media
rm -rf /tmp/tmp*

# flush rabbit queue -- UNTESTED
#sudo -u rabbitmq -c "rabbitmqctl stop_app"
#sudo -u rabbitmq -c "rabbitmqctl reset"
#sudo -u rabbitmq -c "rabbitmqctl start_app"
