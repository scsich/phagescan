# -*- coding: utf_8 -*-
from celery import subtask
from constance import config
from kombu import uuid
import os
import shutil
import datetime
from django.db import models
from django.db.models.query_utils import Q
from nsrl.models import NSRLBloomQuery
from sample.abstract import AbstractFileSample
from scanworker.masterworker import MasterWorkerTask
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from scanworker.result import ScanRunErrorHandlerTask, ScanRunResultHandlerTask, ScanRunFinalizerTask
from virusscan.models import ScanRunResult
import logging
logr = logging.getLogger(__name__)

# converts # of Bytes into something more human-readable
# credit: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size


def sizeof_fmt(num):
	for x in ['bytes', 'KB', 'MB', 'GB']:
		if -1024.0 < num < 1024.0:
			return "{0:3.1f} {1}".format(num, x)
		num /= 1024.0
	return "{0:3.1f} {1}".format(num, 'TB')


class SampleAlreadyExists(Exception):
	def __init__(self, sample_object):
		self.sample_object = sample_object


class FileSampleManager(models.Manager):
	EXPIRATION_DELTA_RESCAN = datetime.timedelta(days=30)

	def samples_for_periodic_rescan(self):
		"""
		Get a list of samples that should be rescanned.

		Currently this means the following:
		* Sample is NOT in NSRL
		* Sample is NOT infected
		* Sample is not more than the EXPIRATION_DELTA_RESCAN
		"""

		# todo central configuration repository/web interface thing for system
		return self.filter(self.get_non_infected_q()). \
			filter(self.nsrl_unknowns_q()). \
			filter(submission_time__gte=datetime.datetime.utcnow() - self.EXPIRATION_DELTA_RESCAN).distinct('pk')

	def get_non_infected_q(self):
		l = ScanRunResult.objects.get_infected().values_list('scan_run__sample', flat=True)
		return ~Q(pk__in=list(l))

	def nsrl_unknowns_q(self):
		# the file same list should be smaller then
		bq = NSRLBloomQuery()
		nsrl_members = [pk for pk, md5 in filter(lambda x: bq.md5_exists(x[1]), self.values_list('pk', 'md5'))]
		return ~Q(pk__in=nsrl_members)

	def _clean_tmp_dir(self):
		# Clean temporary directory
		file_list = os.listdir("/tmp")
		for f in file_list:
			if f.startswith("tmp"):
				uid = os.getuid()
				info = os.stat(os.path.join("/tmp", f))
				if info.st_uid == uid:
					if os.path.isfile(os.path.join("/tmp", f)):
						# Ignore tmp files that can't be removed
						try:
							os.remove(os.path.join("/tmp", f))
						except:
							pass
					else:
						# Ignore tmp files that can't be removed
						try:
							shutil.rmtree(os.path.join("/tmp", f))
						except:
							pass

	def run_search(self, search_string, qs=None):
		# todo strip out search string
		filename_q = Q(other_name__filename__icontains=search_string) | Q(
			scanrun__scanrunresult__metadata__icontains=search_string.lower())
		if qs is None:
			qs = self.all()

		def _str_is_hex(search_str):
			# test is search string contains only valid hex chars
			try:
				int(search_str, 16)
				return True
			except ValueError:
				return False

		if len(search_string) > 18 and _str_is_hex(search_string):
			hash_q = Q(sha256__icontains=search_string) | Q(md5__icontains=search_string)
			filename_q |= hash_q
		qs = qs.filter(filename_q).values('pk').distinct()
		# throwing a weird db exception when done regularly
		return self.filter(pk__in=qs)

	def all_related(self):
		return self.prefetch_related('other_name', 'scanrun_set', 'scanrun_set__scanrunresult_set')

	def create_sample_from_file_and_user(self, f, user, kick_off_scan=False):
		sha256_hash = self.model.filename_hasher(f.read())
		filename = f.name
		logr.debug("Sample received: {0}".format(filename))

		try:
			a = self.get(sha256=sha256_hash)
			a.attach_new_filename(filename or "BLANK_FILENAME")
			a.save()

			raise SampleAlreadyExists(a)

		except ObjectDoesNotExist:

			# reset the read above
			f.seek(0)

			a = FileSample(user=user, sha256=sha256_hash)

			# FileSample object requires a file before it can be saved, so set the hash as the file name.
			a.file.save(sha256_hash, f)

			a.attach_new_filename(filename or "BLANK_FILENAME")
			a.save()

			if kick_off_scan:
				a.rescan()
			return a

		finally:
			self._clean_tmp_dir()
			f.close()


class OtherFileNameManager(models.Manager):
	def create_new_by_filename(self, filename):
		obj, created = self.get_or_create(filename=filename)
		return obj


class OtherFilename(models.Model):
	filename = models.CharField(max_length=254, null=False, blank=False, unique=True)
	first_seen = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField(auto_now=True)
	objects = OtherFileNameManager()


class FileSample(AbstractFileSample):
	user = models.ForeignKey(User)
	other_name = models.ManyToManyField(OtherFilename)
	objects = FileSampleManager()

	def __str__(self):
		return self.filename()

	def generate_virus_total_url(self):
		url_template = "https://www.virustotal.com/en/file/%s/analysis/" % self.sha256
		return url_template

	def filename(self):
		# todo verify that this is logical
		try:
			return self.other_name.filter(pk__lte=self.pk)[0].filename
		except IndexError:
			print("[!] FileSample.Filename Index error. filename going to be: {0}".format(self.pk))
			pass
		except ObjectDoesNotExist:
			print("[!] FileSample.Filename ObjectDoesNotExist error. filename going to be: {0}".format(self.pk))
			pass
		return str(self.pk)

	def all_filenames(self, limit=25):
		return self.other_name.values_list('filename', flat=True)[:limit]

	def get_applicable_scanners(self):
		from scanworker.tasks import VALID_SCANNERS_NO_INSTALL_CHECK

		scanners_to_run = set(VALID_SCANNERS_NO_INSTALL_CHECK())
		return scanners_to_run

	def latest_scan(self):
		return self.scanrun_set.get_latest_pending_completed()

	def pending_scans(self):
		return self.scanrun_set.have_pending_non_expired_scans()

	@property
	def scan_timeout(self):
		"""
		Pull scan run timeout from constance config which can be edited in the admin interface.
		"""
		return config.SCANRUN_TIMEOUT

	def is_infected(self):
		return self.latest_scan().is_infected()

	def get_view_properties(self, err=None):
		d = {
		self.V_NAME_KEY: self.filename(),
		self.V_SIZE_KEY: sizeof_fmt(self.file.size),
		self.V_HASH_KEY: self.file_hash(),

		# todo implement url
		self.V_URL_KEY: self.get_absolute_url(),
		}
		if err:
			d[self.V_ERROR_KEY] = err
		else:
			d[self.V_MSG_KEY] = 'Scan Started'

		return d

	def attach_new_filename(self, filename):
		self.other_name.add(OtherFilename.objects.create_new_by_filename(filename))

	def _get_all_scanning_tasks_and_create_db_entries(self):
		task_id =  str(uuid())

		scan_run = self.scanrun_set.create_pending_scan_run_from_sample( task_id)
		scan_run.save()
		jobs = scan_run.get_scan_tasks_and_create_pending_db_entries(timeout=self.scan_timeout)

		return scan_run, jobs

	def _launch_all_scanning_subtasks_after_task_enum(self, jobs):
		err_handler = ScanRunErrorHandlerTask()
		result_handler = ScanRunResultHandlerTask()
		# filter out none jobs that we don't have to launch

		filt_jobs = filter(lambda jobdb: jobdb[0] is not None, jobs)

		r = [job.apply_async(timeout=self.scan_timeout * 0.9,
		                 link_error=subtask(err_handler, queue=err_handler.queue),
		                 link=subtask(result_handler, args=( db_entry.task_id,), queue=result_handler.queue),
		                 ) for job, db_entry in filt_jobs]
		return r

	def _launch_finializer_task(self, scan_run):
		# todo replace seconds with self.scan_timeout
		return ScanRunFinalizerTask.apply_async(args=[scan_run],
		                                        eta=(datetime.datetime.utcnow() +
		                                             datetime.timedelta(seconds=config.SCANRUN_TIMEOUT)))

	def _launch_all_scanning_subtasks(self):
		scan_run, jobs = self._get_all_scanning_tasks_and_create_db_entries()
		self._launch_all_scanning_subtasks_after_task_enum(jobs)
		self._launch_finializer_task(scan_run)

	def rescan(self, force=False, timeout=None):
		"""
		This method should touch off the MasterWorkerTask which will handle the scan task.

		*Only one master worker per sample should be allowed
		"""
		if not self.scanrun_set.have_pending_non_expired_scans() or force:
			self.save()
			return MasterWorkerTask.apply_async(args=[self], timeout=timeout) if timeout else MasterWorkerTask.apply_async(args=[self])


