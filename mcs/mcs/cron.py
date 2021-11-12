#!/usr/bin/env python
import os
import django
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


def update_refs():
    from refs.rest_truck import thruk_request2df

    thruk_filter = "services?host_name[regex]=^ReFS&display_name[regex]=^Mount:"
    attributes = [
        "host_name",
        "description",
        "display_name",
    ]

    try:
        print("Run update_refs")
        thruk_request2df(thruk_filter, attributes)
    except Exception as e:
        print(e)


def update_customer():
    from explorer.functions import dtln_data2df, df2mcs

    MASTERDATA_SERVER = "dat-ls-masterda.dtln.local"
    MASTERDATA_DB = "masterdata"
    query = "select customer_id as id, customer as name, archive as archived, dt_archive \
                 as archived_datetime from customer"
    column_types = {
        "name": "str",
        "archived": "boolean",
        "archived_datetime": "datetime64[ns]",
    }
    try:
        print("Run update_customer")
        df2mcs(
            dtln_data2df(
                MASTERDATA_SERVER, MASTERDATA_DB, query, column_types, "Customer"
            ),
            "Customer",
        )
    except Exception as e:
        print(e)


def update_contragent_id():
    from explorer.functions import dtln_data2df, df2mcs

    MASTERDATA_SERVER = "dat-ls-masterda.dtln.local"
    MASTERDATA_DB = "masterdata"
    query = "select contragent_id as id, contragent as name, archive as archived, dt_archive as archived_datetime,\
                 customer_id from contragent"
    column_types = {
        "name": "str",
        "archived": "boolean",
        "archived_datetime": "datetime64[ns]",
    }
    try:
        print("Run update_contragent_id")
        df2mcs(
            dtln_data2df(
                MASTERDATA_SERVER, MASTERDATA_DB, query, column_types, "Contragent"
            ),
            "Contragent",
        )
    except Exception as e:
        print(e)


if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mcs.settings")
    django.setup()
    update_refs()
    update_customer()
    update_contragent_id()
