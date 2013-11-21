
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from virusscan.models import ScanRun, ScannerType, FakeMasterScannerType, ScannerTypeWorkerImage
from django.views.generic import ListView, RedirectView
from django.http import HttpResponse
from django.http import Http404
import os


class ScanRunListView(ListView):
	model = ScanRun
	queryset = ScanRun.objects.get_latest_scans_distinct_sample()
	paginate_by = 50

	def dispatch(self, request, *args, **kwargs):
		return super(ScanRunListView, self).dispatch(request, *args, **kwargs)


def serve_xml(self, request, *args, **kwargs):
	response = None
	path = kwargs['document_root'] + request

	if os.path.exists(path):
		xml = open(path, 'r')
		response = HttpResponse(xml.read(), content_type="text/xml")
		return response
	else:
		raise Http404


def serve_text(self, request, *args, **kwargs):
	response = None
	path = kwargs['document_root'] + request

	if os.path.exists(path):
		text = open(path, 'r')
		response = HttpResponse(text.read(), content_type="text/plain")
		return response
	else:
		raise Http404


class ScannerTypeWorkerView(ListView):
	model = ScannerType
	# only get scanners that have scanner types back
	queryset = ScannerType.objects.get_active_scanners_for_display()

	def get_context_data(self, **kwargs):
		ctx =  super(ScannerTypeWorkerView, self).get_context_data(**kwargs)
		from scanworker.masterworker import MasterWorkerTask
		from scanworker.result import ScanRunErrorHandlerTask, ScanRunFinalizerTask, ScanRunResultHandlerTask
		if ScannerType.objects.count() == 0:
			# then we should create everything right quick
			ScannerType.objects.create_all_valid_scanner_db_entries()
		ctx['master_tasks'] = map(FakeMasterScannerType,
		                          [MasterWorkerTask, ScanRunErrorHandlerTask, ScanRunFinalizerTask, ScanRunResultHandlerTask])
		ctx['worker_images'] = ScannerTypeWorkerImage.objects.get_active_worker_images()
		return ctx


class LimitedWorkerActionView(RedirectView):
	@method_decorator(user_passes_test(lambda u: u.is_staff))
	def dispatch(self, request, *args, **kwargs):
		return super(LimitedWorkerActionView, self).dispatch(request, *args, **kwargs)


class WorkerTerminateAllRedirect(LimitedWorkerActionView):

	# must be temporary so browser always does it
	permanent = False

	def get_redirect_url(self, **kwargs):
		ScannerTypeWorkerImage.objects.terminate_all()
		messages.info(self.request, "Purged All Workers, you will have to restart them.")
		return reverse('worker-list')


class WorkerTerminateSingle(LimitedWorkerActionView):

	# must be temporary so browser always does it
	permanent = False

	def get_redirect_url(self, **kwargs):

		obj = get_object_or_404(ScannerTypeWorkerImage, pk = kwargs['pk'])
		if obj.worker_image_exists_in_ec2() and obj.get_running_instances():
			messages.info(self.request, "Terminating EC2 Worker Image {0}.".format(obj.image_label))
			obj.terminate()
		else:
			messages.error(self.request, "No EC2 Worker images to terminate {0}.".format(obj.image_label))
		return reverse('worker-list')


class WorkerStartSingle(LimitedWorkerActionView):

	# must be temporary so browser always does it
	permanent = False

	def get_redirect_url(self, **kwargs):
		obj = get_object_or_404(ScannerTypeWorkerImage, pk = kwargs['pk'])
		messages.info(self.request, "Starting EC2 Single Worker Image {0}.".format(obj.image_label))
		obj.spin_up()
		return reverse('worker-list')
