
from django.contrib import admin
from sample.models import FileSample


class FileSampleAdmin(admin.ModelAdmin):
	pass

admin.site.register(FileSample, FileSampleAdmin)
