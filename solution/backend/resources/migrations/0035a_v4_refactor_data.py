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


def create_category_params(from_obj):
    return {
        "name": from_obj.name or "",
        "description": from_obj.description or "",
        "order": from_obj.order,
        "show_if_empty": from_obj.show_if_empty,
        "old_pk": from_obj.pk,
    }


def copy_categories(OldCategory, OldSubCategory, NewCategory, NewSubCategory):
    # Create a list of subcategories
    subcategories = list(OldSubCategory.objects.all().values_list("pk", flat=True))

    for i in OldCategory.objects.all():
        # Create the parent category
        parent = NewCategory.objects.create(**create_category_params(i))
        # Create all subcategories of the parent, if they exist
        for j in i.sub_categories.all():
            NewSubCategory.objects.create(**{
                **create_category_params(j),
                **{"parent": parent}
            })
            subcategories.remove(j.pk)  # Remove the subcategory from this list so we don't create it twice
    
    # Create subcategories that do not have parents, if they exist
    for i in OldSubCategory.objects.filter(pk__in=subcategories):
        NewSubCategory.objects.create(**create_category_params(i))


def copy_public_categories(apps, schema_editor):
    OldCategory = apps.get_model("resources", "Category")
    OldSubCategory = apps.get_model("resources", "SubCategory")
    PublicCategory = apps.get_model("resources", "PublicCategory")
    PublicSubCategory = apps.get_model("resources", "PublicSubCategory")

    copy_categories(OldCategory, OldSubCategory, PublicCategory, PublicSubCategory)


class Migration(migrations.Migration):
    dependencies = [
        ('resources', '0034_v4_refactor_models'),
    ]

    operations = [
        migrations.RunPython(partial(migration, copy_public_categories)),
    ]
