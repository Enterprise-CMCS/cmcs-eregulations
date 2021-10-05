import datetime

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models

## Category types
# Current choice is one model per level due to constraint of exactly 3 levels.

class Category(models.Model):
    title = models.CharField(max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0, blank=True)
    show_if_empty = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class SubCategory(Category):
    parent = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="sub_categories")


class SubSubCategory(Category):
    parent = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="sub_sub_categories")

## Location models
# Defines where supplemental content is located. All locations must inherit from AbstractLocation.

class AbstractLocation(models.Model):
    title = models.IntegerField()
    part = models.IntegerField()


class Subpart(AbstractLocation):
    subpart_id = models.CharField(max_length=12)

    def __str__(self):
        return f'{self.title} {self.part} Subpart {self.subpart_id}'


class SubjectGroup(AbstractLocation):
    subject_group_id = models.CharField(max_length=512)

    def __str__(self):
        return f'{self.title} {self.part} - {self.subject_group_id}'


class Section(AbstractLocation):
    section_id = models.IntegerField()
    parent = models.ForeignKey(AbstractLocation, null=True, blank=True, on_delete=models.SET_NULL, related_name="children")

    def __str__(self):
        return f'{self.title} {self.part}.{self.section_id}'

## Supplemental content models
# All supplemental content types must inherit from AbstractSupplementalContent.

class AbstractSupplementalContent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="supplemental_content")
    locations = models.ManyToManyField(AbstractLocation, null=True, blank=True, related_name="supplemental_content")


class SupplementalContent(AbstractSupplementalContent):
    title = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(max_length=512, null=True, blank=True)

    date = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Leave blank or enter one of: \"YYYY\", \"YYYY-MM\", or \"YYYY-MM-DD\".",
        validators=[RegexValidator(
            regex="^\\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$",
            message="Date field must be blank or of format \"YYYY\", \"YYYY-MM\", or \"YYYY-MM-DD\"! For example: 2021, 2021-01, or 2021-01-31.",
        )],
    )

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

    def __str__(self):
        return f'{self.date} {self.title} {self.truncated_description}...'

    @property
    def truncated_description(self):
        return (self.description or [])[:50]
