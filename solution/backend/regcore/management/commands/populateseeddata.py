from django.core.management.base import BaseCommand

from common.populate_seed import loadSeedData


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        loadSeedData()
