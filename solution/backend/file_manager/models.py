import os
import uuid

from django.db import models
from model_utils.managers import InheritanceManager

from common.fields import CombinedNaturalSort, VariableDateField
from common.functions import check_string_value
from common.mixins import DisplayNameFieldMixin
from resources.models import AbstractLocation


class DocumentType(models.Model):
    class Meta:
        verbose_name_plural = "Document Types"
    name = models.CharField(max_length=512, null=False, blank=False)
    description = models.CharField(max_length=512, null=False, blank=False)
    order = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class AbstractRepoCategory(models.Model, DisplayNameFieldMixin):
    name = models.CharField(max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0, blank=True)
    show_if_empty = models.BooleanField(default=False)

    objects = InheritanceManager()

    def __str__(self):
        return f"{self.name} ({self._meta.verbose_name})"

    class Meta:
        ordering = ["order", "name"]


class RepositoryCategory(AbstractRepoCategory):

    class Meta:
        verbose_name = "Repository Category"
        verbose_name_plural = "Repository Categories"


class RepositorySubCategory(AbstractRepoCategory):
    parent = models.ForeignKey(RepositoryCategory, on_delete=models.CASCADE, related_name="sub_categories")

    class Meta:
        verbose_name = "Repository Sub-category"
        verbose_name_plural = "Repository Sub-categories"


class Subject(models.Model):
    class Meta:
        verbose_name_plural = "Subjects"
    full_name = models.CharField(max_length=512, null=False, blank=False)
    short_name = models.CharField(max_length=50, null=True, blank=True)
    abbreviation = models.CharField(max_length=10, null=True, blank=True)
    combined_sort = CombinedNaturalSort(['short_name', 'abbreviation', 'full_name'], null=True)

    def __str__(self):
        return f"{self.full_name} {check_string_value(self.short_name)} {check_string_value(self.abbreviation)}"


class Group(models.Model):
    name = models.CharField(max_length=512, null=False, blank=False, unique=True)
    abbreviation = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class Division(models.Model):
    group = models.ForeignKey(Group, blank=True, null=True, related_name="divisions", on_delete=models.SET_NULL)
    name = models.CharField(max_length=512, null=False, blank=False, unique=True)
    abbreviation = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class UploadedFile(models.Model):
    division = models.ForeignKey(Division, blank=True, null=True, related_name="files", on_delete=models.SET_NULL)
    document_name = models.CharField(max_length=512, null=True, blank=True)
    file_name = models.CharField(max_length=512, null=True, blank=True)
    date = VariableDateField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    internal_notes = models.TextField(null=True, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True, related_name="uploads")
    document_type = models.ForeignKey(DocumentType, blank=True, null=True, related_name="uploads", on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        AbstractRepoCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="uploads"
    )
    locations = models.ManyToManyField(AbstractLocation, blank=True, related_name="uploads", verbose_name="Regulation Locations")
    uid = models.UUIDField(
         primary_key=False,
         default=uuid.uuid4,
         editable=False)

    def extension(self):
        _, extension = os.path.splitext(self.file_name)
        return extension

    def get_key(self):
        if self.extension():
            return 'uploaded_files/' + str(self.uid) + self.extension()
        else:
            raise ValueError("File does not have an extension")

    def __str__(self) -> str:
        return str(self.document_name) + ' ' + str(self.summary)
