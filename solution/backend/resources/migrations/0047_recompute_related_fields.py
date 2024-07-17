from django.db import migrations, models
from django.db.models import Value, Q
from django.contrib.postgres.aggregates import ArrayAgg


TIMEOUT_MINUTES = 10


def generate_related(apps, schema_editor):
    schema_editor.execute(f"SET LOCAL statement_timeout TO {TIMEOUT_MINUTES * 60000};")
    AbstractResource = apps.get_model("resources", "AbstractResource")
    for resource in AbstractResource.objects.all():
        groups = resource.resource_groups.all()

        if not groups:
            # This resource does not belong to any groups, so we will treat it differently.
            # Set related_X to contain only the X objects in the individual resource.
            # We must do this for filtering purposes when `group_resources=true` on resource endpoints.
            resource.related_resources.clear()
            resource.related_citations.set(resource.cfr_citations.all())
            resource.related_categories.set([resource.category] if resource.category else [])
            resource.related_subjects.set(resource.subjects.all())
            continue

        AbstractResource.objects.filter(resource_groups__in=groups).update(group_parent=False)
        for group in groups:
            group.resources.filter(pk=group.resources.order_by("-date").first().pk).update(group_parent=True)
        related_resources = AbstractResource.objects.filter(resource_groups__in=groups)
        related_aggregates = related_resources.aggregate(
            all_citations=ArrayAgg("cfr_citations", distinct=True, filter=Q(cfr_citations__isnull=False), default=Value([])),
            all_categories=ArrayAgg("category", distinct=True, filter=Q(category__isnull=False), default=Value([])),
            all_subjects=ArrayAgg("subjects", distinct=True, filter=Q(subjects__isnull=False), default=Value([])),
        )
        related_resources = related_resources.exclude(pk=resource.pk)

        resource.related_resources.set(related_resources)
        resource.related_citations.set(related_aggregates["all_citations"])
        resource.related_categories.set(related_aggregates["all_categories"])
        resource.related_subjects.set(related_aggregates["all_subjects"])


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0046_abstractresource_related_categories_and_more'),
    ]

    operations = [
        migrations.RunPython(generate_related),
    ]
