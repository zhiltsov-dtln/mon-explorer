from django.db import models
from explorer.models import Contragent


class BackupFolder(models.Model):
    # host = models.ForeignKey(ThrukHost, on_delete=models.CASCADE, null=False)
    id = models.CharField("Key Host name+svc", primary_key=True, max_length=255)
    host_name = models.CharField("Nagios Host name", max_length=255)
    # contragent_id = models.CharField("Contragent ID", max_length=255, null=True)
    contragent = models.ForeignKey(Contragent, on_delete=models.SET("None"), null=True)
    # mount_point = models.CharField("mount_point", max_length=255)
    description = models.CharField("Nagios Service name", max_length=255)
    archived = models.BooleanField("Archived or not", null=True)
    archived_datetime = models.DateTimeField("Archived DateTime", null=True)

    def __str__(self):
        if self.host_name:
            return self.host_name
        else:
            return "Unnamed"
