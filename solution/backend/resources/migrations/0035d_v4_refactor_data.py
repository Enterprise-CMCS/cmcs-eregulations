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


def copy_subjects(apps, schema_editor):
    if not apps.is_installed("file_manager"):
        return  # Skip copying repo subjects
    try:
        OldSubject = apps.get_model("file_manager", "Subject")
    except Exception:
        return  # Failed to import needed models, skip copying repo subjects
    NewSubject = apps.get_model("resources", "NewSubject")

    for i in OldSubject.objects.all():
        NewSubject.objects.create(
            full_name=i.full_name or "",
            short_name=i.short_name or "",
            abbreviation=i.abbreviation or "",
            combined_sort=i.combined_sort,
            old_pk=i.pk,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('resources', '0035c_v4_refactor_data'),
    ]

    operations = [
        migrations.RunPython(partial(migration, copy_subjects)),
    ]
