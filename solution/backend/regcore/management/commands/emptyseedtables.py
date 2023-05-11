
from django.core.management.base import BaseCommand

from resources.models import (
    AbstractCategory,
    AbstractResource,
    AbstractLocation,
    FederalRegisterDocumentGroup,
    ResourcesConfiguration,
)

from regcore.search.models import Synonym


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        AbstractResource.objects.all().delete()
        AbstractCategory.objects.all().delete()
        AbstractLocation.objects.all().delete()
        ResourcesConfiguration.objects.all().delete()
        FederalRegisterDocumentGroup.objects.all().delete()
        Synonym.objects.all().delete()
