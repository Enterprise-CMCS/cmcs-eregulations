
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from regcore.search.models import Synonym
from regulations.models import SiteConfiguration, StatuteLinkConverter
from resources.models import (
    AbstractCategory,
    AbstractLocation,
    AbstractResource,
    FederalRegisterDocumentGroup,
    ResourcesConfiguration,
)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        AbstractResource.objects.all().delete()
        AbstractCategory.objects.all().delete()
        AbstractLocation.objects.all().delete()
        ResourcesConfiguration.objects.all().delete()
        FederalRegisterDocumentGroup.objects.all().delete()
        Synonym.objects.all().delete()
        StatuteLinkConverter.objects.all().delete()
        Group.objects.all().delete()
        Permission.objects.all().delete()
        ContentType.objects.all().delete()
        SiteConfiguration.objects.all().delete()
