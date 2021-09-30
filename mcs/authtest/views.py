from authtest import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import logging
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.http import (
    HttpResponse,
    Http404,
    HttpResponseServerError,
    JsonResponse,
    response,
)

from explorer.models import ThrukHost

logger = logging.getLogger(__name__)


def debug(obj):
    logger.info(type(obj))
    logger.info(dir(obj))
    logger.info(obj)


def test(request, *args, **kwargs):
    return HttpResponse("OK it is 8008")


def get_contragent_id(request):
    try:
        mail = request.user.email
        logger.info("!!! MAIL FROM LAIMS is " + str(mail))
        res_id = auth.check_contragent_id(request, mail, retry=0)
        logger.info(res_id)
        return res_id
    except:
        logger.info("Anonymus")
        return render(request, "login.html")


def login(request, *args, **kwargs):
    res_id = get_contragent_id(request)
    context = {"info": res_id}
    return render(request, "login.html", context)


def hosts_paginator(request, paginator_type):
    res_id = get_contragent_id(request)
    logger.info("contragent_id is" + str(res_id["id"]))
    agent_id = str(res_id["id"])

    hosts = ThrukHost.objects.filter(clid_source=agent_id)

    url = "/?"
    search_str = ""
    sort_str = ""

    try:
        page_number = int(request.GET.get("page", 1))
    except ValueError:  # 'page' is not a number
        raise Http404

    search_query = request.GET.getlist("search")
    logger.info("search_query")
    logger.info(search_query)

    if search_query:
        for q in search_query:
            hosts = hosts.filter(name__icontains=q)
            search_str = search_str + "search=" + q + "&"

    sort = request.GET.getlist("filter")
    logger.info("filter")
    logger.info(filter)

    if filter:
        hosts = hosts.order_by(*sort)
        for s in sort:
            sort_str = sort_str + "sort=" + s + "&"
    else:
        d = {}
        try:
            host = ThrukHost.objects.get(id=host_id)
            fields = ThrukHost._meta.get_fields()
            logger.info(getattr(host, "id"))
            for f in fields:
                d[f.verbose_name] = getattr(host, str(f.name))
        except ThrukHost.DoesNotExist:
            raise Http404

    sort = request.GET.getlist("sort")
    logger.info("sort")
    logger.info(sort)

    if sort:
        hosts = hosts.order_by(*sort)
        for s in sort:
            sort_str = sort_str + "sort=" + s + "&"
    else:
        hosts = hosts.order_by("name")

    limit = 50
    paginator = Paginator(hosts, limit)
    url = url + search_str + sort_str
    paginator_url = url + "page="
    paginator.url = paginator_url
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return render(
        request,
        "hosts_paginator.html",
        {
            "paginator": paginator,
            "paginator_type": paginator_type,
            "page": page,
            "hosts_list": page.object_list,
            "info": res_id,
            "search_query": search_query,
            "sort": sort,
        },
    )


def host_page(request, host_id):
    d = {}
    try:
        host = ThrukHost.objects.get(id=host_id)
        fields = ThrukHost._meta.get_fields()
        logger.info(getattr(host, "id"))
        for f in fields:
            d[f.verbose_name] = getattr(host, str(f.name))
    except ThrukHost.DoesNotExist:
        raise Http404
    return render(
        request,
        "host.html",
        {
            "host": host,
            "fields": d,
        },
    )


def host_json(request, host_id):
    d = {}
    try:
        host = ThrukHost.objects.get(id=host_id)
        fields = ThrukHost._meta.get_fields()
        logger.info(getattr(host, "id"))
        for f in fields:
            if f.verbose_name == "clid checked":
                continue
            d[f.verbose_name] = getattr(host, str(f.name))
    except ThrukHost.DoesNotExist:
        raise Http404
    logger.info(d)
    return JsonResponse(d, json_dumps_params={"ensure_ascii": False})
