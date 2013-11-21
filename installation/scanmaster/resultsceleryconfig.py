
## This file is the celeryconfig for the Task Result Handler on scanmaster.
import sys
sys.path.append('.')

import djcelery
djcelery.setup_loader()
from scaggr.settings import *


CELERY_IMPORTS = ('scanworker.result',)
from scanworker.result import get_result_saver_queues
from scanworker.tasks import VALID_SCANNERS as vs
VALID_SCANNERS = vs()
CELERY_QUEUES = get_result_saver_queues()



