import requests
import urllib3
import json

from .models import MountPoint

print("start")
# Request settings
HEADERS = {
    "X-Thruk-Auth-Key": "51eeb551b4e51bbeb6bfdfc98f6a8e650790c0fe6d3b4108b160758d9059e6b3_1"
}
THRUK_ROOT_URL = "https://ostmon.dtln.local/thruk/r/"
# Connection settings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_rest_api_response(request_url):

    try:
        req_res = requests.get(request_url, headers=HEADERS, verify=False, timeout=60)
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error: " + str(errh))
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting: " + str(errc))
    except requests.exceptions.Timeout as errt:
        print("Timeout Error: " + str(errt))
    except requests.exceptions.RequestException as err:
        print("Oops: Something Else: " + str(err))
    else:
        if req_res.status_code == 200:
            result_text = req_res.text.rstrip()
            return result_text
        else:
            print(
                "Incorrect Thruk response: Status Code "
                + str(req_res.status_code)
                + " - "
                + req_res.text
            )
    return ""


def thruk_request2df(records_filter, record_attrs, column_names):
    """Construct URL, make request to Thruk REST API and return Dataframe.

    Args:
        records_filter (String): Part of Thruk REST API URL with Nagios objects (Hosts, Services, Commands, etc) filter
        record_attrs (List): List of requested Nagios object attributes
        column_names (List): List of DataFrame columns names

    Returns:
        DataFrame: Nagios objects DataFrame with attributes
    """
    thruk_rest_api_url = (
        THRUK_ROOT_URL + records_filter + "&columns=" + ",".join(record_attrs)
    )
    res = get_rest_api_response(thruk_rest_api_url)
    dictData = json.loads(res)
    for i in dictData:
        x = MountPoint()
        x.id = i["host_name"] + "." + i["description"]
        x.host_name = i["host_name"]
        x.description = i["description"]
        x.save()
