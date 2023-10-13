from django.core.management.base import BaseCommand

from common.functions import loadSeedData
from content_search.functions import add_to_index
from file_manager.models import UploadedFile
from resources.models import FederalRegisterDocument, SupplementalContent


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        loadSeedData()

        # Temporary way of populating index.  Once index is in prod will add to seed data
        supplemental_content = SupplementalContent.objects.all()
        fr_docs = FederalRegisterDocument.objects.all()
        uploaded_files = UploadedFile.objects.all()

        print('indexing supplemental')
        for sup in supplemental_content:
            add_to_index(sup)

        print('indexing fr')
        for doc in fr_docs:
            add_to_index(doc)

        print('indexing uploaded files')
        for up in uploaded_files:
            add_to_index(up)
