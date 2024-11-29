from django.contrib import admin
from .models import MedicalRecord, PermissionRequest

admin.site.register(MedicalRecord)
admin.site.register(PermissionRequest)
