from django.conf.urls import url
from django.contrib import admin
from .models import MountPoint
from django.http import HttpResponseRedirect
from .functions import thruk_request2df


class MountPointAdmin(admin.ModelAdmin):
    change_list_template = "admin/mount_points_update_list.html"

    def get_urls(self):
        urls = super(MountPointAdmin, self).get_urls()
        custom_urls = [
            url(
                "^import/$",
                self.admin_site.admin_view(self.process_import),
                name="process_import",
            )
        ]
        return custom_urls + urls

    def process_import(self, request):
        thruk_filter = "services?host_name[regex]=^ReFS&display_name[regex]=^Mount:"
        attributes = [
            "host_name",
            "description",
        ]
        columns = [
            "host_name",
            "description",
        ]
        thruk_request2df(thruk_filter, attributes, columns)
        return HttpResponseRedirect("../")

    list_display = ("host_name", "description", "contragent")
    raw_id_fields = ("contragent",)
    autocomplete_lookup_fields = {
        "fk": ["contragent"],
    }


admin.site.register(MountPoint, MountPointAdmin)
