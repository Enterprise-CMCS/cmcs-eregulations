from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import Q, Value
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_jsonform.models.fields import ArrayField

from .internal_resources import (
    InternalFile,
    InternalLink,
)
from .public_resources import (
    FederalRegisterLink,
    PublicLink,
)
from .resources import (
    AbstractInternalResource,
    AbstractPublicResource,
    AbstractResource,
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


def update_related_resources(resource, first=True):
    # Compute the difference between old groups and new groups and process all affected resources.
    # This takes care of the case where the resource was previously in a group, but is now not in that group.
    # We must ensure related fields and parents are updated for all related_resources that currently exist.
    #
    # Note that all_groups and all_resources are cast to lists of pks to avoid issues with the queryset being erased
    # later in this function for reasons unknown.
    new_groups = resource.resource_groups.all()
    q = Q(pk__in=new_groups) | Q(resources__in=resource.related_resources.all())
    all_groups = list(ResourceGroup.objects.filter(q).distinct().values_list("pk", flat=True))
    all_resources = list(AbstractResource.objects.filter(resource_groups__in=all_groups).distinct().values_list("pk", flat=True))

    if first:
        # Set the parent of each affected group (most recent by date at the top of each group's hierarchy)
        AbstractResource.objects.filter(pk__in=all_resources).update(group_parent=False)
        for group in ResourceGroup.objects.filter(pk__in=all_groups):
            group.resources.filter(pk=group.resources.order_by("-date").first().pk).update(group_parent=True)

    # Compute the related resources, citations, categories, and subjects
    # Except for related_resources, these lists are inclusive of the resource we are processing
    if new_groups:
        related_resources = AbstractResource.objects.filter(resource_groups__in=new_groups)
        related_aggregates = related_resources.aggregate(
            all_citations=ArrayAgg("cfr_citations", distinct=True, filter=Q(cfr_citations__isnull=False), default=Value([])),
            all_act_citations=ArrayAgg("act_citations", distinct=True, filter=Q(act_citations__isnull=False), default=Value([])),
            all_usc_citations=ArrayAgg("usc_citations", distinct=True, filter=Q(usc_citations__isnull=False), default=Value([])),
            all_categories=ArrayAgg("category", distinct=True, filter=Q(category__isnull=False), default=Value([])),
            all_subjects=ArrayAgg("subjects", distinct=True, filter=Q(subjects__isnull=False), default=Value([])),
        )
        related_resources = related_resources.exclude(pk=resource.pk)  # Exclude the current resource for related_resources

        # Set related_X fields for this resource
        resource.related_resources.set(related_resources)
        resource.related_citations.set(related_aggregates["all_citations"])
        resource.related_act_citations.set(related_aggregates["all_act_citations"])
        resource.related_usc_citations.set(related_aggregates["all_usc_citations"])
        resource.related_categories.set(related_aggregates["all_categories"])
        resource.related_subjects.set(related_aggregates["all_subjects"])
    else:
        # Set related_X to contain only the X objects in the individual resource.
        # We must do this for filtering purposes when `group_resources=true` on resource endpoints.
        resource.related_resources.clear()
        resource.related_citations.set(resource.cfr_citations.all())
        resource.related_act_citations.set(resource.act_citations.all())
        resource.related_usc_citations.set(resource.usc_citations.all())
        resource.related_categories.set([resource.category] if resource.category else [])
        resource.related_subjects.set(resource.subjects.all())

    if first:
        # For the first resource processed, also update all affected resources (new and old)
        for affected in AbstractResource.objects.filter(pk__in=all_resources):
            update_related_resources(affected, False)


@receiver(post_save, sender=ResourceGroup)
def update_resource_group(sender, instance, **kwargs):
    resources = instance.resources.all()
    if resources:
        update_related_resources(resources.first())


@receiver(post_save, sender=AbstractResource)
@receiver(post_save, sender=AbstractPublicResource)
@receiver(post_save, sender=AbstractInternalResource)
@receiver(post_save, sender=PublicLink)
@receiver(post_save, sender=FederalRegisterLink)
@receiver(post_save, sender=InternalFile)
@receiver(post_save, sender=InternalLink)
def update_group_resources(sender, instance, **kwargs):
    update_related_resources(instance)
