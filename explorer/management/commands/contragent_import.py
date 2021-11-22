from django.core.management.base import BaseCommand
from explorer.admin import ContragentAdmin


class Command(BaseCommand):
    def handle(self, *args, **options):
        ContragentAdmin.process_import(ContragentAdmin, "")
        self.stdout.write(self.style.SUCCESS("Successfully executed"))
