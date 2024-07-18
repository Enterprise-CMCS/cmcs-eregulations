from functools import partial

import common.fields
import common.mixins
import django.core.validators
import django.db.models.deletion
import django_jsonform.models.fields
from django.db import migrations, models
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q


TIMEOUT_MINUTES = 10


def migration(func, apps, schema_editor):
    schema_editor.execute(f"SET LOCAL statement_timeout TO {TIMEOUT_MINUTES * 60000};")
    func(apps, schema_editor)


def copy_resource_groups(apps, schema_editor):
    FederalRegisterDocumentGroup = apps.get_model("resources", "FederalRegisterDocumentGroup")
    ResourceGroup = apps.get_model("resources", "ResourceGroup")
    FederalRegisterLink = apps.get_model("resources", "FederalRegisterLink")

    for i in FederalRegisterDocumentGroup.objects.all():
        # If docket_number_prefixes is a name instead of a prefix, then fill the 'name' field instead.
        if len(i.docket_number_prefixes) == 1 and not i.docket_number_prefixes[0].endswith("-"):
            kwargs = {"name": i.docket_number_prefixes[0]}
        else:
            kwargs = {"common_identifiers": i.docket_number_prefixes}

        group = ResourceGroup.objects.create(**kwargs)

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
        ('resources', '0035g_v4_refactor_data'),
    ]

    operations = [
        migrations.RunPython(partial(migration, copy_resource_groups)),
    ]
