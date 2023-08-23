
from django.db import models
from django.db.models.signals import post_save

from django_jsonform.models.fields import ArrayField
from model_utils.managers import InheritanceManager, InheritanceQuerySet


class UploadedFile(models.Model):
    name = models.CharField(max_length=512, null=True, blank=True)
    file = models.FileField(upload_to='uploaded_files/')
