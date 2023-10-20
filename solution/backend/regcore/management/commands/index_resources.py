from django.core.management.base import BaseCommand

from content_search.functions import index_group
from file_manager.models import UploadedFile
from resources.models import FederalRegisterDocument, SupplementalContent


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        index_group(SupplementalContent.objects.all())
        index_group(FederalRegisterDocument.objects.all())
        index_group(UploadedFile.objects.all())
