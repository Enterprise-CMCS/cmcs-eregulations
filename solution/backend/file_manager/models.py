import os
import uuid

from django.db import models

from common.fields import VariableDateField
from resources.models import AbstractLocation


class UploadCategory(models.Model):
    class Meta:
        verbose_name_plural = "Upload Categories"
    name = models.CharField(max_length=512, null=False, blank=False)
    description = models.CharField(max_length=512, null=False, blank=False)
    order = models.IntegerField()

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=512, null=False, blank=False)
    description = models.CharField(max_length=512, null=False, blank=False)
    order = models.IntegerField()

    def __str__(self):
        return self.name


class UploadedFile(models.Model):
    name = models.CharField(max_length=512, null=True, blank=True)
    file = models.FileField(upload_to='uploaded_files/')
    date = VariableDateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    subject = models.ManyToManyField(Subject, blank=True, related_name="subject")
    categories = models.ManyToManyField(UploadCategory, blank=True, related_name="category")
    locations = models.ManyToManyField(AbstractLocation, blank=True, related_name="locations")
    uid = models.UUIDField(
         primary_key=False,
         default=uuid.uuid4,
         editable=False)

    def filename(self):
        return os.path.basename(self.file.name)
