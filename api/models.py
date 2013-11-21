
from django.contrib.auth.models import User
from django.db import models

KEY_SIZE = 32


class ApiKey(models.Model):
	user = models.ForeignKey(User, related_name='keys')
	key = models.CharField(max_length=KEY_SIZE)

	def save(self, *args, **kwargs):
		self.key = User.objects.make_random_password(length=KEY_SIZE)
		return super(ApiKey, self).save(*args, **kwargs)
