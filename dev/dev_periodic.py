
import sys
sys.path.append('.')

import djcelery
djcelery.setup_loader()
from dev.dev_common import *

CELERY_IMPORTS = ('virusscan.tasks',)
from virusscan.tasks import get_periodic_queues
CELERY_QUEUES = get_periodic_queues()


