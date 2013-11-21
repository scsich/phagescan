
import hashlib
import os


DIGEST_FUNC = hashlib.sha256


class PickleableFileSample(object):

	original_filename = None

	@classmethod
	def file_object_factory(cls, django_file_object, original_filename=None, hex_digest=None):
		# this is so we don't copy or attempt to re-init with an opened file object
		c = cls()
		django_file_object.seek(0)
		c._memory_file_buffer = django_file_object.read()
		c.original_filename = original_filename
		if not hex_digest:
			c.digest = DIGEST_FUNC(c._memory_file_buffer).hexdigest()
		else:
			# remember: 2 chars per hex byte
			assert(len(hex_digest) == DIGEST_FUNC().digest_size*2)
			c.digest = hex_digest

		return c

	@classmethod
	def path_factory(cls, path):
		# create this object from a file path
		with open(path, 'r') as django_file_object:
			inst_file_class = cls.file_object_factory(django_file_object, cls.original_filename)
			inst_file_class.original_filename = os.path.split(path)[1]
			return inst_file_class

	@classmethod
	def string_factory(cls, string_buffer, original_filename = None):
		from cStringIO import StringIO
		return cls.file_object_factory(StringIO(string_buffer), original_filename=original_filename)

	@property
	def all_content(self):
		# todo reference another variable which reads this from a fileserver and not out of memory later
		return self._memory_file_buffer
