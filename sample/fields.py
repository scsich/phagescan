
import hashlib
import django.db.models as models


class Sha256Field(models.SlugField):
	hasher = hashlib.sha256
	length = len(hasher().hexdigest())


class Md5Field(models.CharField):
	hasher = hashlib.md5
	length = len(hasher().hexdigest())


# tell south these things are okay to use
from south.modelsinspector import add_introspection_rules
add_introspection_rules([
	(
		[Sha256Field],  # Class(es) these apply to
		[],             # Positional arguments (not used)
			{           # Keyword argument
			},
	),
], ["^sample\.fields\.Sha256Field"])

add_introspection_rules([
	(
		[Md5Field],     # Class(es) these apply to
		[],             # Positional arguments (not used)
			{           # Keyword argument
		},
	),
], ["^sample\.fields\.Md5Field"])
