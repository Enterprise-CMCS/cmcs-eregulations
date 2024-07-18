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


def copy_resources_config(apps, schema_editor):
    OldResourcesConfiguration = apps.get_model("resources", "ResourcesConfiguration")
    NewResourcesConfiguration = apps.get_model("resources", "NewResourcesConfiguration")
    AbstractPublicCategory = apps.get_model("resources", "AbstractPublicCategory")
    old = OldResourcesConfiguration.objects.first()
    new, _ = NewResourcesConfiguration.objects.get_or_create()
    if old and old.fr_doc_category:
        try:
            new.fr_link_category = AbstractPublicCategory.objects.get(old_pk=old.fr_doc_category.pk)
            new.save()
        except AbstractPublicCategory.DoesNotExist:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ('resources', '0035h_v4_refactor_data'),
    ]

    operations = [
        migrations.RunPython(partial(migration, copy_resources_config)),
    ]
