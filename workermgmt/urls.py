
from django.conf.urls import *
from workermgmt.views import WorkerStatusListView, WorkerTerminateAllRedirect,  WorkerAllMaintainRedirect, WorkerAutoscaleTest, WorkerSpinUpNewRedirect
from django.contrib.auth.decorators import login_required

# from accounts.views import AccountDetailView


# todo require permissions on maintain and refresh
urlpatterns = patterns('',
	#(r'^$', login_required(WorkerStatusListView.as_view()), {}, 'worker-status'),
	#(r'^all/terminate/$', login_required(WorkerTerminateAllRedirect.as_view()), {}, 'worker-all-terminate'),
	#(r'^all/maintain/$', login_required(WorkerAllMaintainRedirect.as_view()), {}, 'worker-all-maintain'),
	#(r'^all/autoscale/$', login_required(WorkerAutoscaleTest.as_view()), {}, 'worker-autoscale'),
)
