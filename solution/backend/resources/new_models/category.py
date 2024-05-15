from django.db import models

from model_utils.managers import InheritanceManager

from common.mixins import DisplayNameFieldMixin


class NewAbstractCategory(models.Model, DisplayNameFieldMixin):
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0, blank=True)
    show_if_empty = models.BooleanField(default=False)

    objects = InheritanceManager()

    def __str__(self):
        return f"{self.name} ({self._meta.verbose_name})"


class PublicCategory(NewAbstractCategory):
    name = models.CharField(max_length=512, unique=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Public Category"
        verbose_name_plural = "Public Categories"


class PublicSubCategory(NewAbstractCategory):
    name = models.CharField(max_length=512, unique=True)
    parent = models.ForeignKey(PublicCategory, on_delete=models.CASCADE, related_name="sub_categories")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Public Subcategory"
        verbose_name_plural = "Public Subcategories"


class InternalCategory(NewAbstractCategory):
    name = models.CharField(max_length=512, unique=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Internal Category"
        verbose_name_plural = "Internal Categories"


class InternalSubCategory(NewAbstractCategory):
    name = models.CharField(max_length=512, unique=True)
    parent = models.ForeignKey(InternalCategory, on_delete=models.CASCADE, related_name="sub_categories")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Internal Subcategory"
        verbose_name_plural = "Internal Subcategories"
