from django.db.models.signals import post_save
from django.dispatch import receiver

from file_manager.models import UploadedFile
from resources.models import FederalRegisterDocument, SupplementalContent

from .functions import add_to_index


@receiver(post_save, sender=FederalRegisterDocument)
@receiver(post_save, sender=SupplementalContent)
@receiver(post_save, sender=UploadedFile)
def add_index(sender, instance, created, **kwargs):
    add_to_index(instance)
