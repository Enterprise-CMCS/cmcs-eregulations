from django.db import migrations, models
from django.db.models import Value, Q
from django.contrib.postgres.aggregates import ArrayAgg


TIMEOUT_MINUTES = 10


def generate_related(apps, schema_editor):
    schema_editor.execute(f"SET statement_timeout = '{TIMEOUT_MINUTES}min';")
    AbstractResource = apps.get_model("resources", "AbstractResource")
    ResourceGroup = apps.get_model("resources", "ResourceGroup")

    for resource in AbstractResource.objects.all():
        new_groups = resource.resource_groups.all()
        q = Q(pk__in=new_groups) | Q(resources__in=resource.related_resources.all())
        all_groups = list(ResourceGroup.objects.filter(q).distinct().values_list("pk", flat=True))
        all_resources = list(AbstractResource.objects.filter(resource_groups__in=all_groups).distinct().values_list("pk", flat=True))

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


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0016_act_abstractresource_act_citations_old_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='abstractresource',
            name='related_act_citations',
            field=models.ManyToManyField(blank=True, to='resources.statutecitation'),
        ),
        migrations.AddField(
            model_name='abstractresource',
            name='related_usc_citations',
            field=models.ManyToManyField(blank=True, to='resources.usccitation'),
        ),
        migrations.RunPython(generate_related, reverse_code=migrations.RunPython.noop),
    ]
