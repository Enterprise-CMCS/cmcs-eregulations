from django.core.exceptions import ValidationError
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
    name = models.CharField(max_length=512)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="subcategories", null=True, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0, blank=True)
    show_if_empty = models.BooleanField(default=False)

    objects = AbstractCategoryManager()

    def __str__(self):
        name = getattr(self, "name", f"Category {self.pk}")
        return f"{name} ({self._meta.verbose_name})"

    def get_category_name_without_annotation(self):
        return self.name


class AbstractPublicCategory(AbstractCategory):
    pass


class PublicCategory(AbstractPublicCategory):
    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if PublicCategory.objects.filter(name__iexact=self.name).exclude(pk=self.pk):
            raise ValidationError(f"Public Category \"{str(self)}\" already exists.")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Public Category"
        verbose_name_plural = "Public Categories"


class PublicSubCategory(AbstractPublicCategory):
    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if PublicSubCategory.objects.filter(name__iexact=self.name).exclude(pk=self.pk):
            raise ValidationError(f"Public SubCategory \"{str(self)}\" already exists.")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Public Subcategory"
        verbose_name_plural = "Public Subcategories"


class AbstractInternalCategory(AbstractCategory):
    pass


class InternalCategory(AbstractInternalCategory):
    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if InternalCategory.objects.filter(name__iexact=self.name).exclude(pk=self.pk):
            raise ValidationError(f"Internal Category \"{str(self)}\" already exists.")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Internal Category"
        verbose_name_plural = "Internal Categories"


class InternalSubCategory(AbstractInternalCategory):
    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if InternalSubCategory.objects.filter(name__iexact=self.name).exclude(pk=self.pk):
            raise ValidationError(f"Internal SubCategory \"{str(self)}\" already exists.")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Internal Subcategory"
        verbose_name_plural = "Internal Subcategories"
