
from django.core.management import call_command
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


def loadSeedData():
    fixtures = [
        ("regulations.siteconfiguration.json", SiteConfiguration),
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
        ("regulations.statutelinkconverter.json", StatuteLinkConverter),
        ("regulations.statutelinkconfiguration.json", StatuteLinkConfiguration),
        # ("cmcs_regulations/fixtures/contenttypes.contenttype.json", ContentType),
        # ("cmcs_regulations/fixtures/auth.permission.json", Permission),
        # ("cmcs_regulations/fixtures/auth.group.json", Group),
    ]

    for fixture in reversed(fixtures):
        fixture[1].objects.all().delete()

    for fixture in fixtures:
        call_command("loaddata", fixture[0])
