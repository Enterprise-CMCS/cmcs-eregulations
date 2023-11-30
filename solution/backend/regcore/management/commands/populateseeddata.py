from django.core.management.base import BaseCommand

from regcore.functions import loadSeedData


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        loadSeedData()
