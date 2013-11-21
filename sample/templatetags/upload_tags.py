
from os import path
from django import template

register = template.Library()

# We do not use the download functionality, but it is hard coded into jquery-fileupload
# in several places, so we are leaving it in.
BASE_DIR = path.dirname(__file__)
UPLOAD_JS_TEMPL = path.join(BASE_DIR, 'upload-js-template.html')
DOWNLOAD_JS_TEMPL = path.join(BASE_DIR, 'download-js-template.html')


@register.simple_tag
def upload_js():
	content = ''
	for fname in [UPLOAD_JS_TEMPL, DOWNLOAD_JS_TEMPL]:
		with open(fname, 'r') as f:
			# Assume comment block is at the start of the file and skip past it.
			content += f.read().split('{% endcomment %}')[1]
	return content

