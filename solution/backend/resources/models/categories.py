from django.db import models
from model_utils.managers import InheritanceManager

from common.mixins import DisplayNameFieldMixin


class NewAbstractCategory(models.Model, DisplayNameFieldMixin):
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0, blank=True)
    show_if_empty = models.BooleanField(default=False)

    objects = InheritanceManager()

    def __str__(self):
        name = getattr(self, "name", f"Category {self.pk}")
        return f"{name} ({self._meta.verbose_name})"


class AbstractPublicCategory(NewAbstractCategory):
    pass


class PublicCategory(AbstractPublicCategory):
    name = models.CharField(max_length=512, unique=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Public Category"
        verbose_name_plural = "Public Categories"


class PublicSubCategory(AbstractPublicCategory):
    name = models.CharField(max_length=512, unique=True)
    parent = models.ForeignKey(PublicCategory, on_delete=models.CASCADE, related_name="subcategories")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Public Subcategory"
        verbose_name_plural = "Public Subcategories"


class AbstractInternalCategory(NewAbstractCategory):
    pass


class InternalCategory(AbstractInternalCategory):
    name = models.CharField(max_length=512, unique=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Internal Category"
        verbose_name_plural = "Internal Categories"


class InternalSubCategory(AbstractInternalCategory):
    name = models.CharField(max_length=512, unique=True)
    parent = models.ForeignKey(InternalCategory, on_delete=models.CASCADE, related_name="subcategories")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Internal Subcategory"
        verbose_name_plural = "Internal Subcategories"
