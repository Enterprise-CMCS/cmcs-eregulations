from django.db import models
from model_utils.managers import (
    InheritanceManager,
)

from common.mixins import DisplayNameFieldMixin


class AbstractCategoryManager(InheritanceManager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            is_fr_link_category=models.ExpressionWrapper(
                ~models.Q(fr_link_category_config=None),
                output_field=models.BooleanField()
            )
        )


class AbstractCategory(models.Model, DisplayNameFieldMixin):
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0, blank=True)
    show_if_empty = models.BooleanField(default=False)

    objects = AbstractCategoryManager()

    def __str__(self):
        name = getattr(self, "name", f"Category {self.pk}")
        return f"{name} ({self._meta.verbose_name})"


class AbstractPublicCategory(AbstractCategory):
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


class AbstractInternalCategory(AbstractCategory):
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
