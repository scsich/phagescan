
## This file is the celeryconfig for the Periodic Task Handler on scanmaster.
import sys
sys.path.append('.')

import djcelery
djcelery.setup_loader()
from scaggr.settings import *


CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_IMPORTS = ('virusscan.tasks',)
from virusscan.tasks import get_periodic_queues

CELERY_QUEUES = get_periodic_queues()
