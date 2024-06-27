from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_jsonform.models.fields import ArrayField

from .resources import AbstractResource


class ResourceGroup(models.Model):
    name = models.CharField(
        max_length=512,
        blank=True,
        help_text="In leiu of (or in addition to) a list of common document identifiers, "
                  "you may specify a name that identifies this group of documents.",
    )
    common_identifiers = ArrayField(
        models.CharField(max_length=512, blank=True),
        default=list,
        blank=True,
        help_text="Common identifiers to use when grouping documents. For example, when grouping Federal Register Documents, "
                  "use the docket number prefix, like \"CMS-1234-\".",
    )
    resources = models.ManyToManyField(AbstractResource, blank=True, related_name="resource_groups")

    def __str__(self):
        if self.name:
            name = self.name
        elif self.common_identifiers:
            name = ", ".join(self.common_identifiers)
        else:
            name = "Empty"
        return f"{name} group"

    class Meta:
        verbose_name = "Resource Group"
        verbose_name_plural = "Resource Groups"
        ordering = ["name", "common_identifiers"]
