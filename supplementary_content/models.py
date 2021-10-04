import datetime

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0, blank=True)
    show_if_empty = models.BooleanField(default=False)


class SubCategory(Category):
    parent = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="sub_categories")


class SubSubCategory(Category):
    parent = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="sub_sub_categories")


class Location(models.Model):
    title = models.IntegerField()
    part = models.IntegerField()

    def __str__(self):
        return f'{self.title} {self.part}'


class Subpart(Location):
    subpart_id = models.CharField(max_length=12)

    def __str__(self):
        return f'{self.title} {self.part} Subpart {self.subpart_id}'


class SubjectGroup(Location):
    subject_group_id = models.CharField(max_length=512)

    def __str__(self):
        return f'{self.title} {self.part} - {self.subject_group_id}'


class Section(Location):
    section_id = models.IntegerField()
    parent = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="children")

    def __str__(self):
        return f'{self.title} {self.part}.{self.section_id}'


class SupplementalContent(models.Model):
    title = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(max_length=512, null=True, blank=True)

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

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="supplemental_content")
    approved = models.BooleanField(default=False)
    locations = models.ManyToManyField(Location, null=True, blank=True, related_name="supplemental_content")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
