
from django.contrib.auth.models import User
from django.db import models
from virusscan.models import ScanRun
from api.models import ApiKey


class Account(models.Model):
	user = models.OneToOneField(User, related_name="account", verbose_name="user", unique=True, null=False)

	def get_scans(self):
		return ScanRun.objects.filter(sample__user=self.user)

	def get_pending_scans(self):
		return ScanRun.objects.get_non_expired_pending_scans()

	def get_samples(self):
		return self.user.filesample_set.all()

	def get_api_key(self):
		apikey = ApiKey.objects.filter(user=self.user)
		key = ""
		if apikey and apikey.count > 0:
			key = apikey[0].key
		else:
			key_obj = ApiKey()
			key_obj.user = self.user
			key_obj.save()
			keys = ApiKey.objects.filter(user=self.user)
			if keys.count > 0:
				key = keys[0].key

		return key
