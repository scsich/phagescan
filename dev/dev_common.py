
from scaggr.settings import *

DEBUG = True

SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}


# scaggr.settings uses postgres as the default database.
# so you do not have to re-define the database
# Here you can re-define the DATABASES to use the settings for your test pg database.
DATABASES = {
	# all the CI agents have a postgres server running locally with the super user set as below
	# if you need to do this on your own postgres install....
	# create user citestsuper createdb superuser password 'sup3rdup3r';

	'default' : {
		'ENGINE'	: HSTORE_SUPPORTING_DB_BACKEND, # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		'NAME'		: 'phagedev', # Or path to database file if using sqlite3.
		'USER'		: 'citestsuper', # Not used with sqlite3.
		'PASSWORD'	: 'sup3rdup3r', # Not used with sqlite3.
		'HOST'		: 'scanmaster', # Set to empty string for localhost. Not used with sqlite3.
		'PORT'		: '5432', # Set to empty string for default. Not used with sqlite3.
	}
}

BROKER_CONF = {
  'uid' 	: 'workeruser',
  'pass' 	: 'longworkerpassword',
  'host' 	: 'scanmaster',
  'port' 	: '5672',
  'vhost' 	: 'phage',
}
BROKER_URL = 'amqp://'+BROKER_CONF['uid']+':'+BROKER_CONF['pass']+'@'+BROKER_CONF['host']+':'+BROKER_CONF['port']+'/'+BROKER_CONF['vhost']

TEMPLATE_DIRS = (
# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
	'templates',)


 # A good logging config for development. Too noisy for production.
# Log files will be written to the PROJECT_ROOT dir.
LOGGING = {
	'version': 1,
	'disable_existing_loggers': True,
	'formatters': {
		'standard': {
			'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
		},
	},
	'handlers': {
		'default': { # for internal logging
			'level': 'DEBUG',
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': 'logs/default.log',
			'maxBytes': 1024*1024*5, # 5MB
			'backupCount': 5,
			'formatter': 'standard',
		},
		'request_handler': { # for url requests
			'level': 'DEBUG',
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': 'logs/django_request.log',
			'maxBytes': 1024*1024*5, # 5MB
			'backupCount': 5,
			'formatter': 'standard',
		},
	},
	'loggers': {
		'': {
			'handlers': ['default'],
			'level': 'DEBUG',
			'propagate': True
		},
		'django.request': {
			'handlers': ['request_handler'],
			'level': 'DEBUG',
			'propagate': False
		},
	}
}

