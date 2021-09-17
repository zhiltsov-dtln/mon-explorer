from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponseRedirect

from .models import (
    Contragent,
    Customer,
    ThrukHost,
)

from .functions import (
    dtln_data2df,
    df2mcs,
    thruk_request2df,
)


MASTERDATA_SERVER = "dat-ls-masterda.dtln.local"
MASTERDATA_DB = "masterdata"

SD_SERVER = "dat-ls-sd.dtln.local"
SD_DB = "sd"

CMDB_SERVER = "dat-ls-amdb.dtln.local"
CMDB_DB = "amdb"

VMREPORTS_SERVER = "vmreports.dtln.local"
VMREPORTS_DB = "DataLineDatawarehouse"


class ObjectAdmin(admin.ModelAdmin):
    """This class adds Import button to admin page for importing data from external sources"""

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

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        context.update(
            {"show_save": False, "show_save_and_continue": False, "show_delete": False}
        )
        return super().render_change_form(request, context, add, change, form_url, obj)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class CustomerAdmin(ObjectAdmin):
    change_list_template = "admin/customer_update_list.html"

    def process_import(self, request):
        query = "select customer_id as id, customer as name, archive as archived, dt_archive \
                 as archived_datetime from customer"
        column_types = {
            "name": "str",
            "archived": "boolean",
            "archived_datetime": "datetime64[ns]",
        }
        df2mcs(
            dtln_data2df(
                MASTERDATA_SERVER, MASTERDATA_DB, query, column_types, "Customer"
            ),
            "Customer",
        )
        return HttpResponseRedirect("../")

    list_display = ("id", "name", "archived", "archived_datetime")
    search_fields = ("name",)
    list_filter = ("name", "archived")
    readonly_fields = ("id", "name", "archived", "archived_datetime")


admin.site.register(Customer, CustomerAdmin)


class ContragentAdmin(ObjectAdmin):
    change_list_template = "admin/contragent_update_list.html"

    def process_import(self, request):
        query = "select contragent_id as id, contragent as name, archive as archived, dt_archive as archived_datetime,\
                 customer_id from contragent"
        column_types = {
            "name": "str",
            "archived": "boolean",
            "archived_datetime": "datetime64[ns]",
        }
        df2mcs(
            dtln_data2df(
                MASTERDATA_SERVER, MASTERDATA_DB, query, column_types, "Contragent"
            ),
            "Contragent",
        )
        return HttpResponseRedirect("../")

    list_display = (
        "id",
        "name",
        "customer_id",
        "customer",
        "archived",
        "archived_datetime",
    )
    list_display_links = ("name", "customer")
    list_filter = ("name", "customer__name", "customer__id", "archived")
    sreadonly_fields = ("id", "name", "customer", "archived", "archived_datetime")
    search_fields = ("name",)


admin.site.register(Contragent, ContragentAdmin)


class ThrukHostAdmin(ObjectAdmin):
    change_list_template = "admin/thrukhost_update_list.html"

    def process_import(self, request):
        thruk_filter = "hosts?"
        attributes = [
            "peer_key",
            "peer_name",
            "name",
            "display_name",
            "alias",
            "address",
            "_HOST_TYPE",
            "_CLID",
            "_CUSTOMER",
            "icon_image_alt",
            "_SUPPORT_GROUP",
            "checks_enabled",
            "check_command",
            "process_performance_data",
            "state",
            "state_type",
            "acknowledged",
            "scheduled_downtime_depth",
        ]
        columns = [
            "peer_key",
            "peer_name",
            "name",
            "display_name",
            "alias",
            "address",
            "host_type",
            "clid_source",
            "customer",
            "icon_image_alt",
            "support_group",
            "checks_enabled",
            "check_command",
            "process_performance_data",
            "state",
            "state_type",
            "acknowledged",
            "scheduled_downtime_depth",
        ]
        df2mcs(thruk_request2df(thruk_filter, attributes, columns), "ThrukHost")
        return HttpResponseRedirect("../")

    list_display = (
        "name",
        "host_type",
        "customer",
        "clid_source",
        "clid_checked",
        "support_group",
    )
    search_fields = ("name",)
    list_filter = (
        "customer",
        "clid_source",
        "clid_checked",
        "host_type",
    )
    readonly_fields = (
        "peer_key",
        "peer_name",
        "name",
        "display_name",
        "alias",
        "address",
        "host_type",
        "clid_source",
        "clid_checked",
        "customer",
        "icon_image_alt",
        "support_group",
    )


admin.site.register(ThrukHost, ThrukHostAdmin)
