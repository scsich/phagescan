
import sys
sys.path.append('.')

import djcelery
djcelery.setup_loader()
from dev.dev_common import *


CELERY_IMPORTS = ('scanworker.result',)
from scanworker.result import get_result_saver_queues
from scanworker.tasks import VALID_SCANNERS as vs
VALID_SCANNERS = vs()
CELERY_QUEUES = get_result_saver_queues()



