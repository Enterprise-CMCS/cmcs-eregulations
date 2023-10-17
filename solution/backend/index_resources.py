#!/usr/bin/env python
import os


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    import django
    django.setup()
    from content_search.functions import add_to_index
    from file_manager.models import UploadedFile
    from resources.models import FederalRegisterDocument, SupplementalContent

    for sup in SupplementalContent.objects.all():
        add_to_index(sup)

    for fr_doc in FederalRegisterDocument.objects.all():
        add_to_index(fr_doc)

    for up_file in UploadedFile.objects.all():
        add_to_index(up_file)
