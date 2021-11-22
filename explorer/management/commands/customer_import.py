from django.core.management.base import BaseCommand
from explorer.admin import CustomerAdmin


class Command(BaseCommand):
    def handle(self, *args, **options):
        CustomerAdmin.process_import(CustomerAdmin, "")
        self.stdout.write(self.style.SUCCESS("Successfully executed"))
