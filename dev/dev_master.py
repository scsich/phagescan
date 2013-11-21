
import sys
sys.path.append('.')

import djcelery
djcelery.setup_loader()
from dev.dev_common import *
from scanworker.masterworker import generate_celery_mastertask_queue

from scanworker.tasks import VALID_SCANNERS as vs


CELERY_IMPORTS = ('scanworker.masterworker', 'scanworker.tasks', 'virusscan.tasks')
#CELERY_ALWAYS_EAGER = True

#CELERY_DEFAULT_QUEUE = 'MasterWorkerTask' #necessary for periodic_task?


VALID_SCANNERS = vs()

CELERY_QUEUES = generate_celery_mastertask_queue()
#CELERY_ROUTES = VALID_SCANNERS.celery_virus_scan_routes()





