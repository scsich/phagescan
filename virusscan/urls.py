
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from virusscan.views import ScanRunListView, ScannerTypeWorkerView, WorkerTerminateAllRedirect, WorkerTerminateSingle, WorkerStartSingle

urlpatterns = patterns('',
	(r'^$', login_required(ScanRunListView.as_view()), {}, 'scan-list'),

	# worker mgmt stuff

	(r'^worker/$', login_required(ScannerTypeWorkerView.as_view()), {}, 'worker-list'),
	(r'^worker/(?P<pk>\d+)/terminate/$', login_required(WorkerTerminateSingle.as_view()), {}, 'worker-terminate-single'),
    (r'^worker/(?P<pk>\d+)/start/$', login_required(WorkerStartSingle.as_view()), {}, 'worker-start-single'),
	(r'^all/terminate/$', login_required(WorkerTerminateAllRedirect.as_view()), {}, 'worker-all-terminate'),

)

