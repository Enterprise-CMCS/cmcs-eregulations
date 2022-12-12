#!/usr/bin/env python
import os
from django.core.management import call_command


def load_data(fixture, model):
    if not model.objects.count():
        call_command("loaddata", fixture)


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    import django
    django.setup()

    from resources.models import (
        Category,
        SubCategory,
        Subpart,
        Section,
        SupplementalContent,
        FederalRegisterDocumentGroup,
        FederalRegisterDocument,
        ResourcesConfiguration,
    )

    from regcore.search.models import Synonym, SearchConfiguration

    load_data("resources.category.json", Category)
    load_data("resources.subcategory.json", SubCategory)
    load_data("resources.subpart.json", Subpart)
    load_data("resources.section.json", Section)
    load_data("resources.supplementalcontent.json", SupplementalContent)
    load_data("resources.federalregisterdocumentgroup.json", FederalRegisterDocumentGroup)
    load_data("resources.federalregisterdocument.json", FederalRegisterDocument)
    load_data("resources.resourcesconfiguration.json", ResourcesConfiguration)
    load_data("search.synonym.json", Synonym)
    load_data("search.searchconfiguration.json", SearchConfiguration)
