#!/bin/bash

# This script is to start the built-in Django web server to use during testing.
#  You have to run this from within an activated virtual environment.

# Copy this script to the project root to run it.

PORT=8000
IP="0.0.0.0"

python manage.py runserver $IP:$PORT

