import os
import uuid

from django.db import models

from common.fields import VariableDateField
from resources.models import AbstractLocation


class DocumentType(models.Model):
    class Meta:
        verbose_name_plural = "Document Types"
    name = models.CharField(max_length=512, null=False, blank=False)
    description = models.CharField(max_length=512, null=False, blank=False)
    order = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class Subject(models.Model):
    class Meta:
        verbose_name_plural = "Subjects"
    full_name = models.CharField(max_length=512, null=False, blank=False)
    short_name = models.CharField(max_length=50, null=True, blank=True)
    abbreviation = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.full_name


class UploadedFile(models.Model):
    document_id = models.CharField(max_length=512, null=True, blank=True)
    file_name = models.CharField(max_length=512, null=True, blank=True)
    date = VariableDateField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    internal_notes = models.TextField(null=True, blank=True)
    subject = models.ManyToManyField(Subject, blank=True, related_name="uploads")
    document_type = models.ForeignKey(DocumentType, blank=True, null=True, related_name="uploads", on_delete=models.SET_NULL)
    locations = models.ManyToManyField(AbstractLocation, blank=True, related_name="uploads", verbose_name="Regulation Locations")
    uid = models.UUIDField(
         primary_key=False,
         default=uuid.uuid4,
         editable=False)

    def extension(self):
        name, extension = os.path.splitext(self.file_name)
        return extension

    def get_key(self):
        if self.extension():
            return 'uploaded_files/' + str(self.uid) + self.extension()
        else:
            raise ValueError("File does not have an extension")

    def __str__(self) -> str:
        return str(self.document_id) + ' ' + str(self.summary)
