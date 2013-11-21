
from sample.models import FileSample
from django.contrib.auth.models import User
from virusscan.models import ScannerType
from piston.handler import BaseHandler
from django.db import IntegrityError
import hashlib


class ScanResultHandler(BaseHandler):

	allowed_methods = ('GET', 'POST')
	model = FileSample

	def read(self, request, filesample_id=None):

		"""
		Returns scan run information on `filesample_id`
		"""

		base = FileSample.objects

		if filesample_id:

			# Pull sample by user and sample id
			sample = None
			result = None

			try:
				sample = base.get(pk=filesample_id, user=request.user)
				result = sample.latest_scan()
			except:
				return {"error" :"Incomplete scan or invalid sample id."}

			completed = sample.scanrun_set.get_latest_completed()
			result_set = completed.scanrunresult_set.values("infected", "infected_string", "scanner_type_id", "metadata", "traceback")

			# Add scanner name to results
			scanner_map = ScannerType.objects
			for item in result_set:
				try:
					scanner = scanner_map.get(pk=item["scanner_type_id"])
					item["scanner_name"] = scanner.name
				except:
					item["scanner_name"] = item["scanner_type_id"]

			# Return scan status, latest results (if any), and sample id
			result_dict = {"status": result.status, "sample_id": result.sample_id, "results": result_set}

			return result_dict
		else:
			return {"error": "No sample id provided."}

	def create(self, request, filesample_id=None):
		"""
		Given a file, creates a FileSample and kicks off scans
		"""
		filename = None
		upload = None

		try:
			filename = request.FILES["sample"].name
			upload = request.FILES["sample"]
		except:
			return {"error": "No file provided"}

		user = User.objects.get(username=request.user)

		m = hashlib.sha256()
		m.update(upload.read())
		sha256_hash = m.hexdigest()

		# Create a new FileSample for the upload
		sample = None
		try:
			sample = FileSample(user=user, sha256=sha256_hash)
			sample.file.save(sha256_hash, upload)
			sample.save()
		except IntegrityError: 
			return {"error": "Sample Already Exists"}
		except:
			return {"error": "General Upload Error"}

		if filename:
			sample.attach_new_filename(filename)

		sample.rescan()

		# Possibly expand this dictionary in the future
		result_dict = {"sample_id": sample.id}

		return result_dict

	def update(self, request, filesample_id=None):
		"""
			The update operation is not permitted currently
		"""

		return {"error": "Update Not Permitted"}

	def delete(self, request, filesample_id=None):
		"""
			The delete operation is not permitted currently
		"""

		return {"error": "Delete Not Permitted"}
