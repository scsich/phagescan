
import datetime
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView
from djcelery.models import WorkerState
from accounts.models import Account
from sample.models import FileSample
from api.models import ApiKey


def get_worker_status():
	return WorkerState.objects.filter(last_heartbeat__gt=datetime.datetime.utcnow() - datetime.timedelta(minutes=10)).count()


class NewApiKey(RedirectView):

	# must be temporary so browser always does it
	permanent = False

	def get_redirect_url(self, **kwargs):
		key = ApiKey.objects.get(user=self.request.user)
		key.save()
		return '/accounts'


class AccountDetailView(DetailView):

	queryset = Account.objects.all()
	model = Account
	context_object_name = 'account'

	def get_object(self, queryset=None):
		account, created = self.model.objects.get_or_create(user=self.request.user)
		return account

	def get_context_data(self, **kwargs):
		context = super(AccountDetailView, self).get_context_data(**kwargs)
		context['samples'] = FileSample.objects.all()
		return context
