#!/usr/bin/env python
import os


def handler(event, context):
    '''
    Indexes resources for environments
    '''
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    import django
    django.setup()
    from content_search.functions import index_group
    from file_manager.models import UploadedFile
    from resources.models import FederalRegisterDocument, SupplementalContent

    index_group(SupplementalContent.objects.filter(approved=True))
    index_group(FederalRegisterDocument.objects.filter(approved=True))
    index_group(UploadedFile.objects.all())
