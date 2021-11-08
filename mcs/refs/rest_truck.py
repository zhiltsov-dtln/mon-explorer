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


def thruk_request2df(records_filter, record_attrs):

    thruk_rest_api_url = (
        THRUK_ROOT_URL + records_filter + "&columns=" + ",".join(record_attrs)
    )
    json_out = get_rest_api_response(thruk_rest_api_url)
    dict_from_json_out = json.loads(json_out)

    exlude_list_for_arhived = BackupFolder.objects.all()

    for svc in dict_from_json_out:
        pgslq_id = svc["host_name"] + svc["description"]
        exlude_list_for_arhived = exlude_list_for_arhived.exclude(id=pgslq_id)
        try:
            pgsql_obj = BackupFolder.objects.get(id=pgslq_id)

            search_agent_id = re.match(
                r"Mount:\s\w+\.\sContragent_id:\s(\d+)", svc["display_name"]
            )
            if search_agent_id:
                if pgsql_obj.contragent_id != int(search_agent_id.group(1)):
                    logger.warning("ID in DB != ID in nagios")
                    pgsql_obj.id_matched = False
                else:
                    pgsql_obj.id_matched = True
            pgsql_obj.actual = True
            pgsql_obj.archived_datetime = None
            pgsql_obj.save()
        except BackupFolder.DoesNotExist:
            new_pgsql_obj = BackupFolder()
            logger.info("HOST Does not exists in DB. Will be add" + str(pgslq_id))

            new_pgsql_obj.id = pgslq_id
            new_pgsql_obj.host_name = svc["host_name"]
            new_pgsql_obj.description = svc["description"]
            new_pgsql_obj.actual = True
            search_agent_id = re.match(
                r"Mount:\s\w+\.\sContragent_id:\s(\d+)", svc["display_name"]
            )
            if search_agent_id:
                new_pgsql_obj.contragent_id = int(search_agent_id.group(1))
            new_pgsql_obj.save()

    exlude_list_for_arhived = exlude_list_for_arhived.exclude(actual=False)

    for remain in exlude_list_for_arhived:
        logger.info(
            "SVC not in Nagios, will be arhivated "
            + str(remain.host_name)
            + str(remain.description)
        )
        remain.actual = False
        remain.archived_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        remain.save()
