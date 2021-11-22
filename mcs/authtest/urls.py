from django.urls import path, include
from .views import test, login, hosts_paginator, host_json, host_page

urlpatterns = [
    path("test/", test),
    path("login/", login),
    path("", hosts_paginator, {"paginator_type": "default"}),
    path("host/<str:host_id>/", host_page),
    path("host/<str:host_id>/json", host_json),
    path("oidc/", include("mozilla_django_oidc.urls")),
]
