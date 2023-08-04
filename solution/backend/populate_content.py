#!/usr/bin/env python
import os

from django.core.management import call_command


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    import django
    django.setup()
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType

    from regcore.search.models import Synonym
    from regulations.models import SiteConfiguration, StatuteLinkConfiguration, StatuteLinkConverter
    from resources.models import (
        AbstractCategory,
        AbstractLocation,
        AbstractResource,
        Category,
        FederalRegisterDocument,
        FederalRegisterDocumentGroup,
        ResourcesConfiguration,
        Section,
        SubCategory,
        Subpart,
        SupplementalContent,
    )

    fixtures = [
        ("resources.abstractcategory.json", AbstractCategory),
        ("resources.category.json", Category),
        ("resources.subcategory.json", SubCategory),
        ("resources.abstractlocation.json", AbstractLocation),
        ("resources.subpart.json", Subpart),
        ("resources.section.json", Section),
        ("resources.abstractresource.json", AbstractResource),
        ("resources.supplementalcontent.json", SupplementalContent),
        ("resources.federalregisterdocumentgroup.json", FederalRegisterDocumentGroup),
        ("resources.federalregisterdocument.json", FederalRegisterDocument),
        ("resources.resourcesconfiguration.json", ResourcesConfiguration),
        ("search.synonym.json", Synonym),
        ("regulations.siteconfiguration.json", SiteConfiguration),
        ("regulations.statutelinkconverter.json", StatuteLinkConverter),
        ("regulations.statutelinkconfiguration.json", StatuteLinkConfiguration),
        ("cmcs_regulations/fixtures/contenttypes.contenttype.json", ContentType),
        ("cmcs_regulations/fixtures/auth.permission.json", Permission),
        ("cmcs_regulations/fixtures/auth.group.json", Group),
    ]

    # First delete all instances of models that we're populating
    for fixture in reversed(fixtures):
        fixture[1].objects.all().delete()

    # Now load the fixtures
    for fixture in fixtures:
        call_command("loaddata", fixture[0])
