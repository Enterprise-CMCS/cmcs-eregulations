from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_jsonform.models.fields import ArrayField

from .resources import (
    AbstractResource,
    AbstractPublicResource,
    AbstractInternalResource,
)

from .public_resources import (
    PublicLink,
    FederalRegisterLink,
)

from .internal_resources import (
    InternalFile,
    InternalLink,
)


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


def update_related_resources(resource):
    groups = resource.resource_groups.all()
    AbstractResource.objects.filter(resource_groups__in=groups).update(group_parent=False)
    for group in groups:
        group.resources.filter(pk=group.resources.order_by("-date").first().pk).update(group_parent=True)
    related_resources = AbstractResource.objects.filter(resource_groups__in=groups).exclude(pk=resource.pk)
    resource.related_resources.set(related_resources)
    for related_resource in related_resources:
        related_groups = related_resource.resource_groups.all()
        related_resources = AbstractResource.objects.filter(resource_groups__in=related_groups).exclude(pk=related_resource.pk)
        related_resource.related_resources.set(related_resources)


@receiver(post_save, sender=ResourceGroup)
def update_resource_group(sender, instance, **kwargs):
    for resource in instance.resources.all():
        update_related_resources(resource)


@receiver(post_save, sender=AbstractResource)
@receiver(post_save, sender=AbstractPublicResource)
@receiver(post_save, sender=AbstractInternalResource)
@receiver(post_save, sender=PublicLink)
@receiver(post_save, sender=FederalRegisterLink)
@receiver(post_save, sender=InternalFile)
@receiver(post_save, sender=InternalLink)
def update_group_resources(sender, instance, **kwargs):
    update_related_resources(instance)
