from django.db import models
from explorer.models import Contragent


class MountPoint(models.Model):
    id = models.CharField("Key Host name+svc", primary_key=True, max_length=255)
    host_name = models.CharField("ThrukHost host name", max_length=255, default="")
    description = models.CharField("Nagios Service name", max_length=255)
    contragent = models.ForeignKey(Contragent, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.host_name} - {self.description}"
