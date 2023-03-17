#!/usr/bin/env python
import os
from django.core.management import call_command


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    import django
    django.setup()

    from resources.models import (
        BaseCategory,
        Location,
        ResourceGroup,
        Resource,
        ResourcesConfiguration,
    )
    from regcore.search.models import Synonym

    fixtures = [
        ("resources.basecategory.json", BaseCategory),
        ("resources.location.json", Location),
        ("resources.resourcegroup.json", ResourceGroup),
        ("resources.resource.json", Resource),
        ("resources.resourcesconfiguration.json", ResourcesConfiguration),
        ("search.synonym.json", Synonym),
    ]

    # First delete all instances of models that we're populating
    for fixture in fixtures:
        fixture[1].objects.all().delete()

    # Now load the fixtures
    for fixture in fixtures:
        call_command("loaddata", fixture[0])
