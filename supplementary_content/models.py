import datetime

from django.core.validators import RegexValidator
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

    date = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Enter one of: \"YYYY\", \"YYYY-MM\", or \"YYYY-MM-DD\".",
        validators=[RegexValidator(
            regex="^\\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$",
            message="Date must be of format \"YYYY\", \"YYYY-MM\", or \"YYYY-MM-DD\"! For example: 2021, 2021-01, or 2021-01-31.",
        )],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="supplementary_content")
    approved = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.date} {self.title} {self.truncated_description}...'

    def clean(self):
        # If a day is entered into the date field, validate for months with less than 31 days.
        if self.date is not None:
            date_fields = self.date.split("-")
            if len(date_fields) == 3:
                (year, month, day) = date_fields
                try:
                    _ = datetime.date(int(year), int(month), int(day))
                except ValueError:
                    raise ValidationError(f'{day} is not a valid day for the month of {month}!')

    @property
    def truncated_description(self):
        return (self.description or [])[:50]


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
