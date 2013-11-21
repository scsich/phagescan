
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, RedirectView
from django.core.urlresolvers import reverse
from django.contrib import messages
from djcelery.models import WorkerState
from workermgmt.util import DjangolessVMManager
import datetime


def get_worker_status():
	return WorkerState.objects.filter(
		last_heartbeat__gt=datetime.datetime.utcnow() - datetime.timedelta(minutes=10)).count()


class WorkerStatusListView(ListView):
	template_name = "workermgmt/workermgmt_list.html"
	paginate_by = 50

	def get_queryset(self):
		d = DjangolessVMManager()
		instances = d.get_worker_instances_all()
		return instances

	def get_context_data(self, **kwargs):
		# todo reflect previous form back?
		d = DjangolessVMManager()
		context = super(WorkerStatusListView, self).get_context_data(**kwargs)
		context['workers_running'] = len(d.get_worker_instances_running())
		context['pending_scans'] = d.get_pending_scans()

		return context

		# todo annotate samples infected and infected string so we don't have to do subqueries for each


class LimitedWorkerActionView(RedirectView):
	@method_decorator(user_passes_test(lambda u: u.is_staff))
	def dispatch(self, request, *args, **kwargs):
		return super(LimitedWorkerActionView, self).dispatch(request, *args, **kwargs)


class WorkerTerminateAllRedirect(LimitedWorkerActionView):

	# must be temporary so browser always does it
	permanent = False

	def get_redirect_url(self, **kwargs):
		d = DjangolessVMManager()
		d.destroy_all_workers()
		messages.info(self.request, "Purged All Workers, you will have to restart them")

		return reverse('worker-status')


class WorkerAllMaintainRedirect(LimitedWorkerActionView):

	# must be temporary so browser always does it
	permanent = False

	def get_redirect_url(self, **kwargs):
		d = DjangolessVMManager()
		d.maintain()
		messages.info(self.request, "Running new worker creation and expired termination")

		return reverse('worker-status')


class WorkerAutoscaleTest(LimitedWorkerActionView):

	# must be temporary so browser always does it
	permanent = False

	def get_redirect_url(self, **kwargs):
		d = DjangolessVMManager()
		autoscale_result = d.autoscale()
		messages.info(self.request, autoscale_result)

		return reverse('worker-status')


class WorkerSpinUpNewRedirect(LimitedWorkerActionView):

	# must be temporary so browser always does it
	permanent = False

	def get_redirect_url(self, **kwargs):
		d = DjangolessVMManager()
		d.spin_up_new_worker()
		messages.info(self.request, "Spinning up a new single worker")

		return reverse('worker-status')
