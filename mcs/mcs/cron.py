#!/usr/bin/env python
import os
import django
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


def execute_command():
    # from refs.models import BackupFolder
    from refs.rest_truck import thruk_request2df

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

    try:
        print("Run shell script")
        thruk_request2df(thruk_filter, attributes, columns)
    except Exception as e:
        print(e)


if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mcs.settings")
    django.setup()
    execute_command()
