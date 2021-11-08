from django.db import models
from explorer.models import Contragent


class BackupFolder(models.Model):
    id = models.CharField("Key Host name+svc", primary_key=True, max_length=255)
    host_name = models.CharField("Nagios Host name", max_length=255)
    contragent = models.ForeignKey(Contragent, on_delete=models.SET("None"), null=True)
    description = models.CharField("Nagios Service name", max_length=255)
    actual = models.BooleanField("Actual or not", null=True)
    archived_datetime = models.DateTimeField("Archived DateTime", null=True)
    id_matched = models.BooleanField("id_matched or not", null=True)

    def __str__(self):
        if self.host_name:
            return self.host_name
        else:
            return "Unnamed"
