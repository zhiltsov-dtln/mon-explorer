import requests
import os
import time
import logging
from django.conf import settings

# logging.basicConfig(filename="test.log", level=logging.INFO)
logger = logging.getLogger(__name__)
url_base = settings.SD_URL
sd_login = settings.SD_LOGIN
sd_password = settings.SD_PWD


def provider_logout(request):
    logout_url = "http://explorer.mon.dtln.local/login/"
    redirect_url = (
        settings.OIDC_BASE_URL
        + "/protocol/openid-connect/logout?redirect_uri="
        + logout_url
    )
    return redirect_url


def generate_new_oapi_token():
    url = url_base + "login"
    headers = {
        "accept": "application/json",
        "login": sd_login,
        "password": sd_password,
        "generate_new_token": "true",
    }
    data = ""
    resp = ""
    try:
        r = requests.post(url, headers=headers, data=data)
    except requests.exceptions.HTTPError as errh:
        logger.error("OAPI SD login HTTP Error: " + str(errh))
        request_rc = "HTTP Error"
    except requests.exceptions.ConnectionError as errc:
        logger.error("OAPI SD login Request Connection Error: " + str(errc))
        request_rc = "Connection Error"
    except requests.exceptions.Timeout as errt:
        logger.error("OAPI SD login Request Timeout Error: " + str(errt))
        request_rc = "Timeout"
    except requests.exceptions.RequestException as err:
        logger.error("OAPI SD login Request Exception: " + str(err))
        request_rc = "Exception"
    else:
        if r.status_code == 200:
            request_rc = "OK"
            resp = r.json()
            logger.info(resp)
            logger.info("Created new token: " + resp["token"])
            os.environ["SD_token"] = resp["token"]
        else:
            logger.error(
                "Incorrect OAPI SD login response: Status Code "
                + str(r.status_code)
                + " - "
                + r.text
            )
            request_rc = "Incorrect Status Code"
        return request_rc


def check_contragent_id(request, mail, retry=0):
    contragent_id_status = {"rc": "", "id": 0, "contragent": ""}
    token = os.getenv("SD_token")

    if token is None:
        generate_new_oapi_token()

    token = os.getenv("SD_token")
    url = url_base + "source?email=" + mail

    headers = {
        "accept": "application/json",
        "token": token,
    }
    data = ""
    try:
        r = requests.get(url, headers=headers, data=data)
    except requests.exceptions.HTTPError as errh:
        logger.error("OAPI SD issue HTTP Error: " + str(errh))
        contragent_id_status["rc"] = "HTTP Error"
    except requests.exceptions.ConnectionError as errc:
        logger.error("OAPI SD issue Request Connection Error: " + str(errc))
        contragent_id_status["rc"] = "Connection Error"
    except requests.exceptions.Timeout as errt:
        logger.error("OAPI SD issue Request Timeout Error: " + str(errt))
        contragent_id_status["rc"] = "Timeout"
    except requests.exceptions.RequestException as err:
        logger.error("OAPI SD issue Request Exception: " + str(err))
        contragent_id_status["rc"] = "Exception"
    else:
        if r.status_code == 200:
            logger.info("Good request, code 200")
            resp = r.json()
            logger.info(resp)
            logger.info(
                "contragent is "
                + str(resp[0]["contragent"])
                + "; contragent_id is "
                + str(resp[0]["contragent_id"])
            )
            contragent_id_status["id"] = resp[0]["contragent_id"]
            contragent_id_status["contragent"] = resp[0]["contragent"]
        elif r.status_code == 500:
            retry += 1
            if retry < 3:
                logger.warning("Error 500. Retrying...")
                logger.info("Retry: " + retry)
                time.sleep(3)
                generate_new_oapi_token()
                contragent_id_status = check_contragent_id(mail, retry)
            else:
                logger.error("500: Internal Error after 3 retries")
                contragent_id_status["rc"] = "Internal Server Error"
        else:
            logger.error(
                "Incorrect OAPI SD issue response: Status Code "
                + str(r.status_code)
                + " - "
                + r.text
            )
            contragent_id_status["rc"] = "Incorrect Status Code"
        return contragent_id_status
