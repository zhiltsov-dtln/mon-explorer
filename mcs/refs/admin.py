from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponseRedirect

from .models import (
    BackupFolder,
)

from .rest_truck import (
    thruk_request2df,
)
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class MyOIDCAB(OIDCAuthenticationBackend):
    def verify_claims(self, claims):
        print(claims)
        verified = super(MyOIDCAB, self).verify_claims(claims) or claims.email_verified
        is_admin = "admin" in claims.get("group", [])
        return verified and is_admin


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
        columns = [
            "host_name",
            "description",
            "display_name",
        ]
        thruk_request2df(thruk_filter, attributes, columns)
        return HttpResponseRedirect("../")

    list_display = (
        "host_name",
        "description",
        "contragent",
        "contragent_id",
        "archived",
        "archived_datetime",
    )
    search_fields = ("host_name",)
    list_filter = ("host_name", "archived")
    readonly_fields = (
        "host_name",
        "description",
        "id",
        "archived",
        "archived_datetime",
    )


admin.site.register(BackupFolder, RefsAdmin)
