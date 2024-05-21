from django.contrib.postgres.aggregates import ArrayAgg
from django.db import migrations
from django.db.models import Q


def copy_resource_groups(apps, schema_editor):
    FederalRegisterDocumentGroup = apps.get_model("resources", "FederalRegisterDocumentGroup")
    ResourceGroup = apps.get_model("resources", "ResourceGroup")
    FederalRegisterLink = apps.get_model("resources", "FederalRegisterLink")

    for i in FederalRegisterDocumentGroup.objects.all():
        group = ResourceGroup.objects.create(
            common_identifiers=i.docket_number_prefixes,
        )

        old_resources = i.documents.all().values_list("pk", flat=True)
        group.resources.set(FederalRegisterLink.objects.filter(old_pk__in=old_resources))
        group.save()

        query = group.resources.all().order_by("-date")
        if not query:
            continue
        first = query[0]

        query = group.resources.aggregate(
            all_citations=ArrayAgg("cfr_citations", distinct=True, filter=Q(cfr_citations__isnull=False)),
            all_subjects=ArrayAgg("subjects", distinct=True, filter=Q(subjects__isnull=False)),
        )

        group.cfr_citations.set(query["all_citations"] or [])
        group.subjects.set(query["all_subjects"] or [])
        group.category = first.category
        group.date = first.date
        group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0040_v4_internal_files'),
    ]

    operations = [
        migrations.RunPython(copy_resource_groups),
    ]
