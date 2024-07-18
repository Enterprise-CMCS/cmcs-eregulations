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


def copy_citations(apps, schema_editor):
    NewSubpart = apps.get_model("resources", "NewSubpart")
    NewSection = apps.get_model("resources", "NewSection")
    OldSubpart = apps.get_model("resources", "Subpart")
    OldSection = apps.get_model("resources", "Section")

    sections = list(OldSection.objects.all().values_list("pk", flat=True))

    for i in OldSubpart.objects.all():
        parent = NewSubpart.objects.create(
            title=i.title,
            part=i.part,
            subpart_id=i.subpart_id,
            old_pk=i.pk,
        )
        for j in i.children.all():
            NewSection.objects.create(
                title=j.title,
                part=j.part,
                section_id=j.section_id,
                old_pk=j.pk,
                parent=parent,
            )
            sections.remove(j.pk)

    for i in OldSection.objects.filter(pk__in=sections):
        NewSection.objects.create(
            title=i.title,
            part=i.part,
            section_id=i.section_id,
            old_pk=i.pk,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('resources', '0035b_v4_refactor_data'),
    ]

    operations = [
        migrations.RunPython(partial(migration, copy_citations)),
    ]
