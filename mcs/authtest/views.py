from django.shortcuts import render
from django.http import HttpResponse
from authtest import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import logging
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


logger = logging.getLogger(__name__)

def debug(obj):
    print(type(obj))
    print(dir(obj))
    print(obj)


def test(request, *args, **kwargs):
    return HttpResponse('OK')


def secure(request, *args, **kwargs):
    return render(request, "login.html")


def login(request, *args, **kwargs):
    try: 
        mail = request.user.email
        logger.info("!!! MAIL FROM CLAIMS is " + str(mail))
        res_id = auth.check_contragent_id(request, mail, retry=0)
        logger.info(res_id)
        context = {'info': res_id}
        return render(request, "login.html", context)
    except:
        logger.info("Anonymus")
        return render(request, "login.html")
    
    

