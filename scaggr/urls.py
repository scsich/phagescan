
## Import the defaults so we get the error conditions too.
#from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from accounts.views import AccountDetailView
from scaggr.settings import DEBUG, MEDIA_ROOT
import api

admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', login_required(AccountDetailView.as_view()), {}),
	url(r'^sample/', include('sample.urls')),
	url(r'^accounts/', include('accounts.urls')),
	url(r'^virusscan/', include('virusscan.urls')),
	url(r'^worker/', include('workermgmt.urls')),
	# todo create  dedicated monitor page to watch queues
	#url(r'^monitor/', include('monitor.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),

	# Uncomment to enable the API
	(r'^api/', include('api.urls'), { 'emitter_format': 'json' }),
)


from virusscan.views import serve_xml, serve_text
from django.views.static import serve
#static serve goes recursive on you, use media_root in settings so we're not scattering path defines all over the place
urlpatterns += patterns('', (r'^media/(.*).xml$', login_required(serve_xml), {'document_root': MEDIA_ROOT}), )
urlpatterns += patterns('', (r'^media/(.*).txt$', login_required(serve_text), {'document_root': MEDIA_ROOT}), )
urlpatterns += patterns('', (r'^media/(.*)$', login_required(serve), {'document_root': MEDIA_ROOT}), )


## This must be last. It only applies when DEBUG=true.
# This will load the static files as defined by STATIC_URL ('/static/')
# without having to worry about having nginx to serve them during dev.
# Remember to run python manage.py collectstatic to populate the /static/ dir.
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

