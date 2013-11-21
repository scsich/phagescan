
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic import CreateView, DeleteView
from django.http import HttpResponse, Http404
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from sample.forms import SimpleSampleSearchForm
from sample.models import FileSample, SampleAlreadyExists
from sample.abstract import SAMPLE_UPLOAD_DIR
import sys
import datetime
import traceback
import logging
logr = logging.getLogger(__name__)

PLAIN_MIMETYPE = 'text/plain'
JSON_MIME_TYPE = "application/json"
SEARCH_FORM = 'search_form'


def response_mimetype(request):
	if JSON_MIME_TYPE in request.META['HTTP_ACCEPT']:
		return JSON_MIME_TYPE
	else:
		return PLAIN_MIMETYPE


def console_debug(f):
	def x(*args, **kw):
		try:
			ret = f(*args, **kw)
		except Exception, e:
			logr.error(str(e))
			exc_type, exc_value, tb = sys.exc_info()
			message = "Type: {0}\nValue: {1}\nTraceback:\n\n{2}".format(exc_type, exc_value, "\n".join(traceback.format_tb(tb)))
			logr.error(message)
			raise
		else:
			return ret
	return x

@console_debug
def multiple_uploader(request):
	if request.POST:
		if request.FILES == None:
			raise Http404("No objects uploaded")

		f = request.FILES['file']
		try:
			a = FileSample.objects.create_sample_from_file_and_user(f, request.user, kick_off_scan=True)
			result = [a.get_view_properties()]

		except SampleAlreadyExists as existing_sample_exception:
			# if we have a duplicate hash we pop an error for the uploader
			so = existing_sample_exception.sample_object
			# todo add more info to result below
			result = [so.get_view_properties(err=FileSample.DUPLICATE_MESSAGE)]

		response_data = simplejson.dumps(result)
		if JSON_MIME_TYPE in request.META['HTTP_ACCEPT']:
			mimetype = JSON_MIME_TYPE
		else:
			mimetype = PLAIN_MIMETYPE
		return HttpResponse(response_data, mimetype=mimetype)
	else:
		return HttpResponse('Only POST accepted')


class SampleRescanRedirect(RedirectView):

	# must be temporary so browser always does it
	permanent = False

	def get_redirect_url(self, **kwargs):
		obj = get_object_or_404(FileSample, sha256=kwargs['slug'])
		messages.info(self.request, "{0} Re-scanning Sample {1}".format(datetime.datetime.utcnow(), obj.sha256))
		obj.rescan(force=True)
		return reverse('sample-detail', kwargs={'slug': obj.sha256})


class SampleDetailView(DetailView):
	model = FileSample
	slug_field = 'sha256'
	context_object_name = 'sample_object'

	def get_object(self, **kwargs):
		return super(SampleDetailView, self).get_object(**kwargs)

	def get(self, request, *args, **kwargs):
		return super(SampleDetailView, self).get(request, *args, **kwargs)


class SampleListView(ListView):
	model = FileSample
	queryset = FileSample.objects.all_related()
	paginate_by = 50

	def get_queryset(self):
		qs =  super(SampleListView, self).get_queryset().order_by('-submission_time')
		search_form = SimpleSampleSearchForm(self.request.GET)

		if search_form.is_valid():
			search_string = search_form.cleaned_data.get('search_string')
			qs = self.model.objects.run_search(search_string, qs=qs)

		return qs

	def get_context_data(self, **kwargs):
		context =  super(SampleListView, self).get_context_data(**kwargs)
		search_form = SimpleSampleSearchForm(self.request.GET)

		if search_form.is_valid():
			context[SEARCH_FORM] = search_form
		else:
			context[SEARCH_FORM] = SimpleSampleSearchForm()

		return context
	# todo annotate samples infected and infected string so we don't have to do subqueries for each


class MySampleListView(SampleListView):
	model = FileSample
	queryset = None
	paginate_by = 50

	def get_queryset(self):
		qs =  super(MySampleListView, self).get_queryset()
		return qs.filter(user=self.request.user)


class SampleCreateView(CreateView):
	model = FileSample

	def dispatch(self, request, *args, **kwargs):
		response = super(SampleCreateView, self).dispatch(request, *args, **kwargs)
		return response

	def form_valid(self, form):
		f = self.request.FILES.get('file')
		self.object = FileSample.objects.create_sample_from_file_and_user(f, form.request.user)
		d = self.object.get_view_properties()
		d.update({
					'url'			: "{0}{1}{2}".format(settings.MEDIA_URL, SAMPLE_UPLOAD_DIR, f.name.replace(" ", "_")),
					'delete_url'	: reverse('upload-delete', args=[self.object.id]),
					'delete_type'	: "DELETE"	})
		response = JSONResponse([d], {}, response_mimetype(self.request))
		response['Content-Disposition'] = 'inline; filename=files.json'
		return response


# class SampleDeleteView(DeleteView):
# 	model = FileSample
#
# 	def delete(self, request, *args, **kwargs):
# 		"""
# 		This does not actually delete the file, only the database record.  But
# 		that is easy to implement.
# 		"""
# 		self.object = self.get_object()
# 		self.object.delete()
# 		response = JSONResponse(True, {}, response_mimetype(self.request))
# 		response['Content-Disposition'] = 'inline; filename=files.json'
# 		return response


class JSONResponse(HttpResponse):
	"""
	JSON response class
	"""
	def __init__(self, obj='', json_opts={}, mimetype=JSON_MIME_TYPE, *args, **kwargs):
		content = simplejson.dumps(obj, **json_opts)
		super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)
