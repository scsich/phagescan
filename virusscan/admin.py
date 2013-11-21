
from virusscan.models import ScanRun, ScanRunResult, ScannerType, ScannerTypeWorkerImage
from django.contrib import admin


class ScanRunAdmin(admin.ModelAdmin):
	pass


class ScanRunResultAdmin(admin.ModelAdmin):
	list_display = ('scan_run', 'scanner_type', 'traceback')


class ScannerTypeAdmin(admin.ModelAdmin):
	list_display = ('name', 'platform')


class ScannerTypeWorkerImageAdmin(admin.ModelAdmin):
	list_display = ('image_label', 'needed_copies')


admin.site.register(ScanRun, ScanRunAdmin)
admin.site.register(ScannerType, ScannerTypeAdmin)
admin.site.register(ScanRunResult, ScanRunResultAdmin)
admin.site.register(ScannerTypeWorkerImage, ScannerTypeWorkerImageAdmin)
