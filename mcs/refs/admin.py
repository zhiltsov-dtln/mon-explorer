from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponseRedirect

from .models import (
    BackupFolder,
)

from .rest_truck import (
    thruk_request2df,
)


class ObjectAdmin(admin.ModelAdmin):
    """This class adds Import button to admin page for importing data from external sources"""

    raw_id_fields = ("contragent",)
    autocomplete_lookup_fields = {
        "fk": ["contragent"],
    }

    def get_urls(self):
        urls = super(ObjectAdmin, self).get_urls()
        custom_urls = [
            url(
                "^import/$",
                self.admin_site.admin_view(self.process_import),
                name="process_import",
            )
        ]
        return custom_urls + urls


class RefsAdmin(ObjectAdmin):

    change_list_template = "admin/thrukhost_update_list.html"

    def process_import(self, request):
        thruk_filter = "services?host_name[regex]=^ReFS&display_name[regex]=^Mount:"  # "hosts?name[regex]=^ReFS"  # host_name=ReFS-NORD02"  #
        attributes = [
            "host_name",
            "description",
            "display_name",
        ]
        thruk_request2df(thruk_filter, attributes)
        return HttpResponseRedirect("../")

    list_display_links = ("description",)
    list_display = (
        "host_name",
        "description",
        "contragent",
        "contragent_id",
        "display_name",
        "actual",
        "archived_datetime",
        "id_matched",
    )
    search_fields = ("description", "contragent")
    list_filter = ("host_name", "actual", "id_matched")
    readonly_fields = (
        "host_name",
        "description",
        "id",
        "actual",
        "archived_datetime",
        "id_matched",
        "display_name",
    )


admin.site.register(BackupFolder, RefsAdmin)
