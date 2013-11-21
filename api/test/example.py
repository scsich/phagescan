
from httplib import HTTPConnection
import mimetypes
import random
import string


class ApiInterface():

	# Custom HTTP Headers
	auth_header = "X-Authorization"
	user_header = "X-User"

	def __init__(self, user_name, auth_key, scan_host, scan_port):

		"""
		Constructor sets the connection info
		The API key for a user can be found on PhageScan's Account page
		"""

		self.user = str(user_name)
		self.api_key = str(auth_key)
		self.port = str(scan_port)
		self.host = str(scan_host)

	def submit_sample(self, file_path):

		"""
		Given a file path, submit a sample to PhageScan
		Returns JSON message with a sample id number (usable to retrieve scan results) or error message
		"""

		body, headers = self.encode_multipart_data({"sample": file_path})


		conn = HTTPConnection("{0}:{1}".format(self.host,self.port))
		conn.request("POST", "/api/upload/", body, headers)

		result = conn.getresponse().read()

		return result

	def get_results(self, sample_id):

		"""
		Given a sample id, get results (if any)
		Output is JSON formatted
		"""

		headers = {self.auth_header : self.api_key, self.user_header : self.user}
		conn = HTTPConnection("{0}:{1}".format(self.host,self.port))
		conn.request("GET", "/api/scanresult/" + str(sample_id), "", headers)

		result = conn.getresponse().read()

		return result

	def encode_multipart_data(self, files):

		"""
		Helper function that forms the HTTP body and headers
		"""

		boundary = self.random_string (30)

		def get_content_type(filename):
			return mimetypes.guess_type (filename)[0] or 'application/octet-stream'

		def encode_file(field_name):
			filename = files [field_name]
			return ('--{0}'.format(boundary),
					'Content-Disposition: form-data; name="{0}"; filename="{1}"'.format(field_name, filename),
					'Content-Type: {0}'.format(get_content_type(filename)),
					'', open(filename, 'rb').read())

		lines = []
		for name in files:
			lines.extend (encode_file (name))
		lines.extend (('--{0}--'.format(boundary), ''))
		body = '\r\n'.join(lines)

		headers = {'content-type': 'multipart/form-data; boundary={0}'.format(boundary),
				   'content-length': str(len (body))}
		headers["Accept"] = "text/json"
		headers[self.auth_header] = self.api_key
		headers[self.user_header] = self.user

		return body, headers

	def random_string(self, length):

		"""
		Helper function to generate the boundary
		"""

		return ''.join(random.choice (string.letters) for ii in range(length + 1))
