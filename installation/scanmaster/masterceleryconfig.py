
## This file is the celeryconfig for the Task Master on scanmaster.
import sys
sys.path.append('.')

import djcelery
djcelery.setup_loader()
from scaggr.settings import *
from scanworker.masterworker import generate_celery_mastertask_queue
from scanworker.tasks import VALID_SCANNERS as vs

CELERY_IMPORTS = ('scanworker.masterworker', 'scanworker.tasks', 'virusscan.tasks')
VALID_SCANNERS = vs()
CELERY_QUEUES = generate_celery_mastertask_queue()
