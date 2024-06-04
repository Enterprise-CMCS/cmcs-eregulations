from django.core.exceptions import ValidationError
from django.db import models
from model_utils.managers import InheritanceManager

from common.mixins import DisplayNameFieldMixin


class AbstractCitation(models.Model, DisplayNameFieldMixin):
    title = models.IntegerField()
    part = models.IntegerField()

    objects = InheritanceManager()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Subpart(AbstractCitation):
    subpart_id = models.CharField(max_length=12)

    def __str__(self):
        return f"{self.title} CFR {self.part} Subpart {self.subpart_id}"

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

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if Section.objects.filter(title=self.title, part=self.part, section_id=self.section_id).exclude(pk=self.pk):
            raise ValidationError(f"Citation \"{str(self)}\" already exists.")

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        ordering = ["title", "part", "section_id"]
