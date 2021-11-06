import requests, urllib3, json, re, logging
from datetime import datetime
from .models import BackupFolder

logger = logging.getLogger(__name__)
logger.info("start")
# Request settings
HEADERS = {
    "X-Thruk-Auth-Key": "51eeb551b4e51bbeb6bfdfc98f6a8e650790c0fe6d3b4108b160758d9059e6b3_1"
}
THRUK_ROOT_URL = "https://ostmon.dtln.local/thruk/r/"
# Connection settings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_rest_api_response(request_url):
    logger.info(f"Making Thruk REST API request with url: {request_url}")
    try:
        req_res = requests.get(request_url, headers=HEADERS, verify=False, timeout=60)
    except requests.exceptions.HTTPError as errh:
        logger.error("HTTP Error: " + str(errh))
    except requests.exceptions.ConnectionError as errc:
        logger.error("Error Connecting: " + str(errc))
    except requests.exceptions.Timeout as errt:
        logger.error("Timeout Error: " + str(errt))
    except requests.exceptions.RequestException as err:
        logger.error("Oops: Something Else: " + str(err))
    else:
        if req_res.status_code == 200:
            result_text = req_res.text.rstrip()
            return result_text
        else:
            logger.error(
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
    x = BackupFolder()
    all = BackupFolder.objects.all()
    for i in dictData:
        try:
            obj = BackupFolder.objects.get(id=(i["host_name"] + i["description"]))
            all = all.exclude(id=(i["host_name"] + i["description"]))
            # logger.info(
            #   str(obj.host_name)
            #  + str(obj.description)
            # + " ID = "
            # + str(obj.contragent_id)
            # )
            res = re.match(r"Mount:\s\w+\.\sContragent_id:\s(\d+)", i["display_name"])
            if res:
                obj.contragent_id = int(res.group(1))
            obj.archived = False
            obj.save()
        except BackupFolder.DoesNotExist:
            logger.info(
                "HOST Does not exists in DB. Will be add"
                + str(i["host_name"] + str(i["description"]))
            )
            all = all.exclude(id=(i["host_name"] + i["description"]))
            x.id = i["host_name"] + i["description"]
            x.host_name = i["host_name"]
            x.description = i["description"]
            x.archived = False
            res = re.match(r"Mount:\s\w+\.\sContragent_id:\s(\d+)", i["display_name"])
            if res:
                x.contragent_id = int(res.group(1))
            x.save()
    for a in all:
        logger.info(
            "SVC not in Nagios, will be arhivated "
            + str(a.host_name)
            + str(a.description)
        )
        a.archived = True
        a.archived_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        a.save()
