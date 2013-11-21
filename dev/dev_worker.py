
import sys
sys.path.append('.')
from dev.dev_common import *


BROKER_CONF['host'] = 'scanmaster'
BROKER_URL = 'amqp://'+BROKER_CONF['uid']+':'+BROKER_CONF['pass']+'@'+BROKER_CONF['host']+':'+BROKER_CONF['port']+'/'+BROKER_CONF['vhost']


CELERY_IMPORTS = ('scanworker.tasks',)
from scanworker.tasks import VALID_SCANNERS as vs
VALID_SCANNERS = vs()
CELERY_QUEUES = VALID_SCANNERS.celery_virus_scan_queues_install_check

#CELERY_ROUTES = VALID_SCANNERS.celery_virus_scan_routes()



