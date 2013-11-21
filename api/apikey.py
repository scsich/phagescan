
from django.http import HttpResponse
from models import ApiKey


class ApiKeyAuthentication(object):

	def is_authenticated(self, request):
		auth_string = request.META["HTTP_X_AUTHORIZATION"]
		user_string = request.META["HTTP_X_USER"]

		if not auth_string:
			return False

		key = None
		try:
			key = ApiKey.objects.get(key=auth_string)
		except:
			return False

		if not key:
			return False

		if user_string != key.user.username:
			return False

		request.user = key.user

		return True

	def challenge(self):
		resp = HttpResponse("Authorization Required")
		resp['WWW-Authenticate'] = "Key Based Authentication"
		resp.status_code = 401
		return resp
