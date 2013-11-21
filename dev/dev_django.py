
import sys
from django.conf import settings
sys.path.append('.')
settings.configure()
from dev.dev_common import *

from scanworker.masterworker import generate_celery_mastertask_queue
CELERY_QUEUES = generate_celery_mastertask_queue()





