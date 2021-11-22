from django.contrib import admin
from .models import MountPoint


class MountPointAdmin(admin.ModelAdmin):
    list_display = ("host_name", "description", "contragent")


admin.site.register(MountPoint, MountPointAdmin)
