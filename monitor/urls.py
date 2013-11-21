
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from monitor.views import MonitorListView

urlpatterns = patterns('',
	(r'^$', login_required(MonitorListView.as_view()), {}, 'monitor-list'),
)

