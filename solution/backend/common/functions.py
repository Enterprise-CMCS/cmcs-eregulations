import boto3
from boto3 import client as boto3_client
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from rest_framework_simplejwt.tokens import RefreshToken

from content_search.models import ContentIndex
from file_manager.models import DocumentType, Subject
from regcore.search.models import Synonym
from regulations.models import (
    RegulationLinkConfiguration,
    SiteConfiguration,
    StatuteLinkConfiguration,
    StatuteLinkConverter,
)
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
        ("regulations.regulationlinkconfiguration.json", RegulationLinkConfiguration),
        ("regulations.statutelinkconverter.json", StatuteLinkConverter),
        ("regulations.statutelinkconfiguration.json", StatuteLinkConfiguration),
        ("file_manager.documenttype.json", DocumentType),
        ("file_manager.subject.json", Subject),
        ("cmcs_regulations/fixtures/contenttypes.contenttype.json", ContentType),
        ("cmcs_regulations/fixtures/auth.permission.json", Permission),
        ("cmcs_regulations/fixtures/auth.group.json", Group),
    ]
    # The vector column for the search index has issues with using seed data.  As in it takes forever.
    # We remove the column first, then we add it back after fixtures are done.

    file_index = ContentIndex.objects.all()
    for con in file_index:
        con.locations.clear()
        con.subjects.clear()
        con.save()
    file_index._raw_delete(file_index.db)
    for fixture in reversed(fixtures):
        fixture[1].objects.all().delete()

    for fixture in fixtures:
        call_command("loaddata", fixture[0])


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def establish_client(client_type):
    if settings.USE_AWS_TOKEN:
        return boto3.client(client_type,
                            aws_access_key_id=settings.S3_AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.S3_AWS_SECRET_ACCESS_KEY,
                            region_name="us-east-1")
    else:
        return boto3.client(client_type, region_name="us-east-1")
