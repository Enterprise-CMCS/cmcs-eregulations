#!/usr/bin/env python
import os
from django.core.management import call_command


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    import django
    django.setup()

    fixtures = [
        "regulations.siteconfiguration.json",
        "regcore.parserconfiguration.json",
        "resources.category.json",
        "resources.subcategory.json",
        "resources.subpart.json",
        "resources.section.json",
        "resources.supplementalcontent.json",
        "resources.federalregisterdocumentgroup.json",
        "resources.federalregisterdocument.json",
        "resources.resourcesconfiguration.json",
        "search.synonym.json",
    ]

    call_command("flush", interactive=False)  # Reset the database before loading any fixtures
    for fixture in fixtures:
        call_command("loaddata", fixture)
