
from django.conf.urls.defaults import *
from piston.resource import Resource
from handlers import ScanResultHandler
from apikey import ApiKeyAuthentication

key_auth = ApiKeyAuthentication()


def ProtectedResource(handler):
    return Resource(handler=handler, authentication=key_auth)

result_handler = ProtectedResource(ScanResultHandler)

urlpatterns = patterns('',
	url(r'^scanresult/(?P<filesample_id>.*)$', result_handler, {'emitter_format': 'json'}),
	url(r'^upload/', result_handler, {'emitter_format': 'json'}),
)
