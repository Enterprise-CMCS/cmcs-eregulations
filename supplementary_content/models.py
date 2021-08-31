from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='sub_categories',
    )
    title = models.CharField(max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.title


class SupplementaryContent(models.Model):
    url = models.URLField(unique=True, max_length=512)
    title = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    day = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="supplementary_content")
    approved = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.date} {self.title} {self.truncated_description}...'

    @property
    def truncated_description(self):
        return (self.description or [])[:50]
    
    @property
    def date(self):
        return (f'{self.year}-' if self.year else '') + \
            (f'{self.month:02d}-' if self.month else '') + \
            (f'{self.day:02d}' if self.day else '')

    def clean(self):
        super().clean()
        if self.day is not None and (self.month is None or self.year is None):
            raise ValidationError("When day is defined, month and year must also be defined!")
        elif self.month is not None and self.year is None:
            raise ValidationError("When month is defined, year must also be defined!")


class RegulationSection(models.Model):
    title = models.CharField(max_length=16)
    part = models.CharField(max_length=16)
    subpart = models.CharField(max_length=32, null=True, blank=True)
    section = models.CharField(max_length=16)
    supplementary_content = models.ManyToManyField(SupplementaryContent, related_name="sections", blank=True)

    def __str__(self):
        return f'{self.title} {self.part}.{self.section}'

    class Meta:
        unique_together = ("title", "part", "section")
