
# This file defines the Celery variables that are common to the
# Task-Master and the Worker(s).

CELERY_RESULT_BACKEND 			= 'amqp'
CELERYD_CONCURRENCY             = 2
CELERYD_PREFETCH_MULTIPLIER     = 1
CELERY_TASK_TIME_LIMIT          = 100
CELERY_DEFAULT_QUEUE 			= 'default'
CELERY_DISABLE_RATE_LIMITS      = True
CELERY_DEFAULT_EXCHANGE 		= 'tasks'
CELERY_DEFAULT_EXCHANGE_TYPE 	= 'topic'
BROKER_HEARTBEAT                = True
CELERY_DEFAULT_ROUTING_KEY 		= 'task.default'
CELERY_ROUTES = {
					'scanworker.masterworker.MasterWorkerTask': {
						'queue'			: 'MasterWorkerTask',
						'routing_key'	: 'MasterWorkerTask'
					},
				}
