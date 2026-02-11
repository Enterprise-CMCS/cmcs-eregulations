import re

from django.core.exceptions import ValidationError
from django.db import models
from model_utils.managers import InheritanceManager

from common.mixins import DisplayNameFieldMixin
from common.fields import NaturalSortField


class AbstractCitation(models.Model, DisplayNameFieldMixin):
    title = models.IntegerField()
    part = models.IntegerField()
    child_id = models.CharField(max_length=12)

    objects = InheritanceManager()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["title", "part", "child_id"]


class Subpart(AbstractCitation):
    subpart_id = models.CharField(max_length=12)

    def __str__(self):
        return f"{self.title} CFR {self.part} Subpart {self.subpart_id}"

    def save(self, *args, **kwargs):
        self.child_id = self.subpart_id
        super().save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if Subpart.objects.filter(title=self.title, part=self.part, subpart_id=self.subpart_id).exclude(pk=self.pk):
            raise ValidationError(f"Citation \"{str(self)}\" already exists.")

    class Meta:
        verbose_name = "Subpart"
        verbose_name_plural = "Subparts"
        ordering = ["title", "part", "subpart_id"]


class Section(AbstractCitation):
    section_id = models.IntegerField()
    parent = models.ForeignKey(Subpart, null=True, blank=True, on_delete=models.SET_NULL, related_name="children")

    def __str__(self):
        return f"{self.title} CFR {self.part}.{self.section_id}"

    def save(self, *args, **kwargs):
        # Ensure child_id is zero-padded to 12 digits. (12 is arbitrary, but it is the max length of the field.)
        # int() ensures that the value is an integer, because even though the field is an IntegerField,
        # it can be passed as a string to the model during create or update.
        self.child_id = f"{int(self.section_id):012d}"
        super().save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if Section.objects.filter(title=self.title, part=self.part, section_id=self.section_id).exclude(pk=self.pk):
            raise ValidationError(f"Citation \"{str(self)}\" already exists.")

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        ordering = ["title", "part", "section_id"]


class Act(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def clean(self):
        self.name = self.name.strip()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Act"
        verbose_name_plural = "Acts"
        ordering = ["name"]


class StatuteCitation(models.Model):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, related_name="statute_citations")
    section = models.CharField(max_length=32)
    section_sort = NaturalSortField("section")

    def clean(self):
        self.section = re.sub(r"\s", "", self.section)

    def __str__(self):
        return f"{self.act.name} §{self.section}"

    class Meta:
        verbose_name = "Statute Citation"
        verbose_name_plural = "Statute Citations"
        unique_together = ("act", "section")
        ordering = ["act__name", "section_sort"]


class UscCitation(models.Model):
    title = models.IntegerField()
    section = models.CharField(max_length=32)
    section_sort = NaturalSortField("section")

    def clean(self):
        self.section = re.sub(r"\s", "", self.section)

    def __str__(self):
        return f"{self.title} USC §{self.section}"

    class Meta:
        verbose_name = "USC Citation"
        verbose_name_plural = "USC Citations"
        unique_together = ("title", "section")
        ordering = ["title", "section_sort"]
