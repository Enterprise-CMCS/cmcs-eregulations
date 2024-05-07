from django.db import models
from django.db.models import Q
from django.contrib.postgres.aggregates import ArrayAgg

from . import NewAbstractResource


class ResourceGroup(NewAbstractResource):
    name = models.CharField(max_length=512, blank=True)
    common_identifiers = ArrayField(
        models.CharField(max_length=512, blank=True),
        default=list,
        blank=True,
        help_text="Common identifiers to use when grouping resources. For example, when grouping Federal Register Documents, "
                  "use the docket number prefix, like \"CMS-1234-\".",
    )
    resources = models.ManyToManyField(NewAbstractResource, blank=True, related_name="groups")

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
        ordering = ("name", "common_identifiers")


def update_group(group):
    post_save.disconnect(post_save_group, sender=ResourceGroup)
    post_save.disconnect(post_save_group_resources, sender=NewAbstractResource)
    try:
        query = group.resources.all().order_by("-date")
        if not query:
            return
        first = query[0]

        query = group.resources.aggregate(
            all_citations=ArrayAgg("citations", distinct=True, filter=Q(citations__isnull=False)),
            all_subjects=ArrayAgg("subjects", distinct=True, filter=Q(subjects__isnull=False)),
        )

        group.citations.set(query["all_citations"])
        group.subjects.set(query["all_subjects"])
        group.category = first.category
        group.date = first.date
        group.save()

    finally:
        post_save.connect(post_save_group, sender=ResourceGroup)
        post_save.connect(post_save_group_resources, sender=NewAbstractResource)


@receiver(post_save, sender=ResourceGroup)
def post_save_group(sender, instance, **kwargs):
    update_group(instance)


@receiver(post_save, sender=NewAbstractResource)
def post_save_group_resources(sender, instance, **kwargs):
    for i in instance.groups.all():
        update_group(i)
