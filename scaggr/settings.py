
import os
import datetime
import djcelery
djcelery.setup_loader()

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += ('constance.context_processors.config',)

CELERY_IMPORTS = ('scanworker.masterworker', 'scanworker.tasks', 'virusscan.tasks')

PENDING_EXPIRE = datetime.timedelta(minutes=10)

# Where files output from a scanrun are saved.
ARTIFACT_SAVE_DIR = 'artifacts/'
# Where image files output from a scanrun are saved.
IMAGE_SAVE_DIR = 'imageout/'
# Where uploaded file samples are stored
SAMPLE_UPLOAD_DIR = 'samples/'
# Depth of samples directory
MAX_SHA256_DIRECTORY_DEPTH=4

# key for celery worker queue cache
QUEUE_WORKER_CACHE_KEY = 'workers'

# for teamcity CI
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# test runner gets confused with django NOSE if you're just inside of Pycharm
if os.getenv('TEAMCITY_PROJECT_NAME') is None:
	del TEST_RUNNER

SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
		'LOCATION': 'cache',
	}
}

BROKER_CONF = {
	'uid'   : 'phagemasteruser',
	'pass'  : 'longmasterpassword',
	'host'	: 'scanmaster',
	'port'	: '5672',
	'vhost'	: 'phage',
}
BROKER_URL = 'amqp://'+BROKER_CONF['uid']+':'+BROKER_CONF['pass']+'@'+BROKER_CONF['host']+':'+BROKER_CONF['port']+'/'+BROKER_CONF['vhost']

SESSION_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

CONSTANCE_CONFIG = {
	'SCANRUN_TIMEOUT' : (60, "Maximum amount of time a single scan run (multiple scanners) is allowed to run"),
	'YARA_REPO_URL' : ('https://github.com/scsich/mass-yara-test', "Git repository URL that houses yara signatures"),
	'YARA_REPO_TYPE' : ('git', "Source control system for the yara repo. Only git and hg are accepted."),
	'IMAGE_MAPPING_DEF_KEY' : ('default', "Default key to use for image mapping"),
	'DEFAULT_WORKER_IMAGE_MAPPING' : ('ubuntu-image', "Default image for scanworker that doesn't have a custom scanner image set"),
	'Panda_EC2_IMAGE' : ('windowsxp-image', "Default image for Panda AV Scanner, notice lowercase prefix of key"),
	'Symantec_EC2_IMAGE' : ('centos-image', "Default image for Symantec AV Scanner, notice lowercase prefix of key"),
	'NUMBER_OF_WORKER_IMAGES_PER_SCANNER' : (2, "Number of worker images to spin up per scanner type"),
	'EC2_URL' : ("http://10.0.0.1:8773/services/Cloud", "URL to EC2-like API or EC2 Itself"),
	'EC2_SECRET' : ("1234567890abcdef1234567890abcde", "Secret"),
	'EC2_ACCESS' : ("1234567890abcdef1234567890abcde", "Access Hash"),
	'EC2_TIMEOUT' : (5, "The amount of time it takes an EC2 connection to timeout"),
	'EC2_USERDATA' : ("#cloud-config\nmanage_etc_hosts: True", "User data to pass to cloud-init"),
	'EC2_KEYPAIR' : ("stacky", "The label for the EC2 Keypair")
}
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

DEBUG = True
ALLOWED_HOSTS = ['*']
#ALLOWED_HOSTS = ['wwwhost.example.com']

ADMINS = (
# ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

HSTORE_SUPPORTING_DB_BACKEND='django.db.backends.postgresql_psycopg2'

DATABASES = {
		'default' : {
				'ENGINE'	: HSTORE_SUPPORTING_DB_BACKEND, # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
				'NAME'		: 'phage', # Or path to database file if using sqlite3.
				'USER'		: 'citestsuper', # Not used with sqlite3.
				'PASSWORD'	: 'sup3rdup3r', # Not used with sqlite3.
				'HOST'		: 'localhost', # Set to empty string for localhost. Not used with sqlite3.
				'PORT'		: '5432', # Set to empty string for default. Not used with sqlite3.
		},
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Etc/UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'us-en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir) )
# os.getcwd() will return the actual root of the project. Not the directory containing this file.
PROJECT_ROOT = os.getcwd()
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'hyctu8mu)j!1usz8t2ol=o@00^6eqx(sy4w+hd-f^f!df7ina*'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
	#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	# 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'scaggr.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'scaggr.wsgi.application'

TEMPLATE_DIRS = (
# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
	os.path.join(PROJECT_ROOT, 'templates')
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	# for migrations
	'south',
	'constance.backends.database',
	'constance', # for live settings to showup in the admin
	# nose should come after south, so nose test is used instead of south test.
	'django_nose',

	'accounts',
	'sample',
	'virusscan',
	'scanworker',
	'djcelery',
	'api',
	'workermgmt',
	'gunicorn',
	'nsrl',
	# Uncomment the next line to enable the admin:
	'django.contrib.admin',
	#'monitor',
	# Uncomment the next line to enable admin documentation:
	# 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
#LOGGING = {
#	'version': 1,
#	'disable_existing_loggers': False,
#	'filters': {
#		'require_debug_false': {
#			'()': 'django.utils.log.RequireDebugFalse'
#		}
#	},
#	'handlers': {
#		'mail_admins': {
#			'level': 'ERROR',
#			'filters': ['require_debug_false'],
#			'class': 'django.utils.log.AdminEmailHandler'
#		}
#	},
#	'loggers': {
#		'django.request': {
#			'handlers': ['mail_admins'],
#			'level': 'ERROR',
#			'propagate': True,
#			},
#	}
#}
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
CELERYD_HIJACK_ROOT_LOGGER = False
if not os.path.isdir(LOG_DIR):
	os.mkdir(LOG_DIR)

LOGGING = {
	'version': 1,
		'disable_existing_loggers': False,
		'formatters': {
				'verbose': {
						'format': '%(asctime)s [%(levelname)s] %(name)s %(module)s %(lineno)d %(process)d %(message)s'
				},
				'standard': {
						'format': '%(asctime)s [%(levelname)s] %(name)s %(lineno)d %(message)s'
				},
				'simple': {
						'format': '%(asctime)s %(levelname)s %(message)s'
				},
		},
		'filters': {
				'require_debug_false': {
						'()': 'django.utils.log.RequireDebugFalse'
				}
		},
		'handlers': {
				'null': {
						'level': 'DEBUG',
						'class': 'django.utils.log.NullHandler',
				},
				'default': {
						'level': 'DEBUG',
						'formatter': 'standard',
						'class': 'logging.handlers.RotatingFileHandler',
						'filename': 'logs/django_debug.log',
						'maxBytes': 1024*1024*5, # 5MB
						'backupCount': 2,
				},
				'request_handler': {
						'level': 'DEBUG',
						'formatter': 'standard',
						'class': 'logging.handlers.RotatingFileHandler',
						'filename': 'logs/django_request.log',
						'maxBytes': 1024*1024*5, # 5MB
						'backupCount': 2,
				},
				'console': {
						'level': 'DEBUG',
						'formatter': 'standard',
						'class': 'logging.StreamHandler'
				},
		},
		'loggers': {
				'django': {
						'handlers': ['null'],
						'level': 'INFO',
						'propagate': True,
				},
				'django.request': {
						'handlers': ['request_handler'],
						'level': 'INFO',
						'propagate': True,
				},
				'celery.redirected': {
						'handlers': ['default'],
						'level': LOG_LEVEL,
						'propagate': False,
				},
				'celery.worker': {
						'handlers': ['default'],
						'level': LOG_LEVEL,
						'propagate': False,
				},
				'': {
						'handlers': ['default'],
						'level': LOG_LEVEL,
						'propagate': False,
				},
		},
		'root': {
				'handlers': ['console'],
				'level': LOG_LEVEL,
		},
}

from scanworker.commonconfig import *
