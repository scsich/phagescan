
from django.contrib.auth.decorators import login_required
from accounts.views import AccountDetailView, NewApiKey
from django.conf.urls import *
from django.contrib.auth.urls import urlpatterns as auth_url_patterns

urlpatterns = patterns('',
	(r'^$', login_required(AccountDetailView.as_view()), {}, 'account'),
	(r'^generate/$', login_required(NewApiKey.as_view()), {}, 'generate-key'),
)

urlpatterns += auth_url_patterns
