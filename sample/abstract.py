
import os
import hashlib
from django.db import models
from sample.fields import Md5Field, Sha256Field
from scanworker.file import PickleableFileSample
from scaggr.settings import SAMPLE_UPLOAD_DIR, MAX_SHA256_DIRECTORY_DEPTH


def generate_hash_directories(hash_str):
	return "/".join([d for d in hash_str[:MAX_SHA256_DIRECTORY_DEPTH]])


def get_hashed_filename_path_and_set_filename(instance, filename):
	new_filename = instance.sha256
	# todo confirm that this gets the proper upload dir off the instance
	dir_path = "{0}{1}".format(instance.UPLOAD_DIR, generate_hash_directories(new_filename))
	return os.path.join(dir_path, new_filename)


class AbstractFileSample(models.Model):
	UPLOAD_DIR			= SAMPLE_UPLOAD_DIR
	DUPLICATE_MESSAGE	= 'duplicateSHA256'
	V_NAME_KEY			= 'name'
	V_SIZE_KEY			= 'size'
	V_HASH_KEY			= 'hash'
	V_ERROR_KEY			= 'error'
	V_URL_KEY			= 'url'
	V_MSG_KEY			= 'msg'

	md5 			= Md5Field(max_length=Md5Field.length, null=False, unique=True)
	sha256 			= Sha256Field(max_length=Sha256Field.length, null=False, unique=True)
	submission_time = models.DateTimeField(auto_now_add=True)
	file 			= models.FileField(upload_to=get_hashed_filename_path_and_set_filename)

	@property
	def file_content(self):
		# todo think about memory caching this
		self.file.seek(0)
		return self.file.read()

	def file_hash(self):
		return str(self.sha256)

	@models.permalink
	def get_absolute_url(self):
		return ('sample-detail',(), {'slug' : self.sha256 })

	@classmethod
	def filename_hasher(cls, file_content):
		return hashlib.sha256(file_content).hexdigest()

	def get_pickleable_file(self):
		return PickleableFileSample.file_object_factory(self.file)

	def save(self, *args, **kwargs):
		# make sure we do our required hashing before we save this thing
		for hash_field_obj, model, direct, m2m in [self._meta.get_field_by_name('md5'),
		                                           self._meta.get_field_by_name('sha256')]:
			if not getattr(self, hash_field_obj.name):
				digest = hash_field_obj.hasher(self.file_content).hexdigest()
				setattr(self, hash_field_obj.name, digest)
		return super(AbstractFileSample, self).save(*args, **kwargs)

	class Meta:
		abstract = True
