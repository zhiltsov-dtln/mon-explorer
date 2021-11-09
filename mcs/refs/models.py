from django.db import models
from explorer.models import Contragent


class BackupFolder(models.Model):
    id = models.CharField("Key Host name+svc", primary_key=True, max_length=255)
    host_name = models.CharField("Nagios Host", max_length=255)
    contragent = models.ForeignKey(Contragent, on_delete=models.SET("None"), null=True)
    description = models.CharField("Nagios Service", max_length=255)
    display_name = models.CharField("Nagios Display Name", max_length=255, null=True)
    actual = models.BooleanField("Actual/Archived ", null=True)
    archived_datetime = models.DateTimeField("Archived Timestamp", null=True)
    id_matched = models.BooleanField("Id Matched in Nagios", null=True)

    def __str__(self):
        if self.host_name:
            return self.host_name
        else:
            return "Unnamed"
