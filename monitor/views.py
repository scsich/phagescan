
from djcelery.models import  WorkerState
from django.views.generic import ListView
import datetime


class MonitorListView(ListView):
	model = WorkerState
	queryset = WorkerState.objects.filter(last_heartbeat__gte=datetime.datetime.utcnow() - datetime.timedelta(minutes=5))

	# todo paginate the list so we don't dump everything

	def dispatch(self, request, *args, **kwargs):
		return super(MonitorListView, self).dispatch(request, *args, **kwargs)



