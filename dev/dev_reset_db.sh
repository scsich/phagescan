#!/bin/bash


# this drops the scaggr DB completely, rebuilds with superuser: devuser/devpass
# run it from the root scaggr directory

DB_NAME="phage"

sudo -u postgres psql -c "drop database $DB_NAME;"
sudo -u postgres psql -c "create database $DB_NAME owner citestsuper;"
sudo -u postgres psql -d $DB_NAME -c "create extension hstore;"

cp dev/dev_db_creds.json initial_data.json
python manage.py syncdb --settings=scaggr.settings_dev --noinput
rm initial_data.json

python manage.py migrate --settings=scaggr.settings_dev

