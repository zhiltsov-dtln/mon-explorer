from django.db import models


class Customer(models.Model):
    id = models.IntegerField("Customer Id", primary_key=True)
    name = models.CharField("Customer Name", max_length=255)
    archived = models.BooleanField("Archived or not")
    archived_datetime = models.DateTimeField("Archived DateTime", null=True)

    def __str__(self):
        return self.name if self.name else "Unnamed"


class Contragent(models.Model):
    id = models.IntegerField("Contragent Id", primary_key=True)
    name = models.CharField("Contragent Name", max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    archived = models.BooleanField("Archived or not")
    archived_datetime = models.DateTimeField("Archived DateTime", null=True)

    def __str__(self):
        return self.name if self.name else "Unnamed"


class ThrukHost(models.Model):
    id = models.CharField("Thruk Host Key", primary_key=True, max_length=255)
    peer_key = models.CharField("Thruk peer key", max_length=16)
    peer_name = models.CharField("Thruk peer name", max_length=16)
    name = models.CharField("Nagios host name", max_length=255)
    display_name = models.CharField("Nagios host display name", max_length=255)
    alias = models.CharField("Nagios host alias", max_length=255)
    address = models.CharField("Nagios host address", max_length=255)
    host_type = models.CharField("Nagios _HOST_TYPE", max_length=32, null=True)
    clid_source = models.IntegerField("CLID", null=True)
    clid_checked = models.ForeignKey(Contragent, on_delete=models.CASCADE, null=True)
    customer = models.CharField("Nagios _CUSTOMER", max_length=255, null=True)
    support_group = models.CharField("SD Support Group", max_length=255, null=True)
    icon_image_alt = models.CharField("Responsible Group", max_length=255, null=True)
    checks_enabled = models.IntegerField("Is Check enabled")
    check_command = models.CharField("Check Command", max_length=255, null=True)
    process_performance_data = models.IntegerField("Is Performance Data collecting")
    state = models.IntegerField("State Severity")
    state_type = models.IntegerField("State Type")
    acknowledged = models.IntegerField("Is Acknowledged")
    scheduled_downtime_depth = models.IntegerField("Downtime Depth", null=True)
    archived = models.BooleanField("Archived or not", null=True)
    archived_datetime = models.DateTimeField("Archived DateTime", null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return "Unnamed"
