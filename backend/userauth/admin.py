from django.contrib import admin
from .models import User, Doctor, Hospital

admin.site.register(User)
admin.site.register(Doctor)
admin.site.register(Hospital)