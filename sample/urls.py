
from django.conf.urls import *
from sample.views import SampleCreateView, multiple_uploader, SampleListView, MySampleListView, SampleDetailView, SampleRescanRedirect
from django.contrib.auth.decorators import login_required


urlpatterns = patterns('',
	(r'^$', login_required(MySampleListView.as_view()), {}, 'my-sample-list'),
	(r'^detail/(?P<slug>[a-fA-F0-9]{64})/$', login_required(SampleDetailView.as_view()), {}, 'sample-detail'),
	(r'^detail/(?P<slug>[a-fA-F0-9]{64})/scan/$', login_required(SampleRescanRedirect.as_view()), {}, 'sample-rescan'),

	(r'^all/$', login_required(SampleListView.as_view()), {}, 'all-sample-list'),
	(r'^new/$', login_required(SampleCreateView.as_view()), {}, 'upload-new'),
	(r'^new/add/$', login_required(multiple_uploader), {}, 'upload-add'),
	(r'^delete/(?P<pk>\d+)$', login_required(SampleCreateView.as_view()), {}, 'upload-delete'),
)

