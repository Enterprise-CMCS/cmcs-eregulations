from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from file_manager.models import UploadedFile
from resources.models import FederalRegisterDocument, SupplementalContent

from .functions import add_to_index
from .models import ContentIndex


@receiver(post_delete, sender=SupplementalContent)
@receiver(post_delete, sender=FederalRegisterDocument)
@receiver(post_delete, sender=UploadedFile)
def delete_index(sender, instance, *args, **kwargs):
    ci = None
    try:
        if isinstance(instance, SupplementalContent):
            ci = ContentIndex.objects.get(supplemental_content=instance)
        elif isinstance(instance, FederalRegisterDocument):
            ci = ContentIndex.objects.get(fr_doc=instance)
        elif isinstance(instance, UploadedFile):
            ci = ContentIndex.objects.get(file=instance)
        if ci:
            ci.delete()
    except ContentIndex.DoesNotExist:
        return



@receiver(post_save, sender=FederalRegisterDocument)
@receiver(post_save, sender=SupplementalContent)
@receiver(post_save, sender=UploadedFile)
def add_index(sender, instance, created, **kwargs):
    add_to_index(instance)



