from django.core.management.base import BaseCommand

from resources.models import FederalRegisterDocument, SupplementalContent


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        content = SupplementalContent.objects.all()[:100]
        SupplementalContent.objects.exclude(pk__in=content).delete()
        content = FederalRegisterDocument.objects.all()[:100]
        FederalRegisterDocument.objects.exclude(pk__in=content).delete()
