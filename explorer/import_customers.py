#!/usr/bin/env python3

from functions import (
    dtln_data2df,
    df2mcs,
)


def process_import():
    masterdata_server = "dat-ls-masterda.dtln.local"
    masterdata_db = "masterdata"

    query = "select customer_id as id, customer as name, archive as archived, dt_archive \
                as archived_datetime from customer"
    column_types = {
        "name": "str",
        "archived": "boolean",
        "archived_datetime": "datetime64[ns]",
    }
    df2mcs(
        dtln_data2df(masterdata_server, masterdata_db, query, column_types, "Customer"),
        "Customer",
    )


if __name__ == "__main__":
    process_import()
