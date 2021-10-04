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
    parent = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="sub_sub_categories")


class Location(models.Model):
    title = models.IntegerField()
    part = models.IntegerField()


class Subpart(Location):
    subpart_id = models.CharField(max_length=12)


class SubjectGroup(Location):
    subject_group_id = models.TextField()


class Section(Location):
    parent = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="children")
    section_id = models.IntegerField()


class SupplementalContent(models.Model):
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="supplemental_content")
    locations = models.ManyToManyField(Location, null=True, blank=True, related_name="supplemental_content")
