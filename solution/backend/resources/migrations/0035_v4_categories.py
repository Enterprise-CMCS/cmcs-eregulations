from django.db import migrations


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


def copy_internal_categories(apps, schema_editor):
    if not apps.is_installed("file_manager"):
        return  # Skip copying repo categories
    try:
        RepoCategory = apps.get_model("file_manager", "RepositoryCategory")
        RepoSubCategory = apps.get_model("file_manager", "RepositorySubCategory")
    except Exception:
        return  # Failed to import needed models, skip copying repo categories

    InternalCategory = apps.get_model("resources", "InternalCategory")
    InternalSubCategory = apps.get_model("resources", "InternalSubCategory")

    copy_categories(RepoCategory, RepoSubCategory, InternalCategory, InternalSubCategory)


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0034_v4_refactor_models'),
    ]

    operations = [
        migrations.RunPython(copy_public_categories),
        migrations.RunPython(copy_internal_categories),
    ]
