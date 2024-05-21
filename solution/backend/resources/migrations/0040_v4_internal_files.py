from django.db import migrations


def copy_internal_files(apps, schema_editor):
    if not apps.is_installed("file_manager"):
        return  # Skip copying repo files
    try:
        UploadedFile = apps.get_model("file_manager", "UploadedFile")
    except Exception:
        return  # Failed to import needed models, skip copying repo files

    InternalFile = apps.get_model("resources", "InternalFile")
    NewSubject = apps.get_model("resources", "NewSubject")
    AbstractCitation = apps.get_model("resources", "AbstractCitation")
    AbstractInternalCategory = apps.get_model("resources", "AbstractInternalCategory")

    categories = AbstractInternalCategory.objects.in_bulk(field_name="old_pk")

    for i in UploadedFile.objects.all():
        file = InternalFile.objects.create(
            old_pk=i.pk,
            approved=True,
            category=categories[i.category.pk] if i.category else None,
            editor_notes=i.internal_notes or "",
            document_id=i.document_name or "",
            summary=i.summary or "",
            created_at=i.updated_at,
            updated_at=i.updated_at,
            date=i.date or "",
            file_name=i.file_name or "",
            uid=i.uid,
        )

        file.cfr_citations.set(AbstractCitation.objects.filter(old_pk__in=i.locations.all().values_list("pk", flat=True)))
        file.subjects.set(NewSubject.objects.filter(old_pk__in=i.subjects.all().values_list("pk", flat=True)))
        file.save()


def throw_exception(apps, schema_editor):
    raise Exception("oops")


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0039_v4_fedreg_links'),
    ]

    operations = [
        migrations.RunPython(copy_internal_files),
    ]
