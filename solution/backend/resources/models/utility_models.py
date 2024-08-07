from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class SingleStringModel(models.Model):
    value = models.TextField(blank=True)

    def __str__(self):
        return self.value


@receiver(post_save, sender=SingleStringModel)
def save_resource(sender, instance, **kwargs):
    if instance.resource:
        instance.resource.save()
