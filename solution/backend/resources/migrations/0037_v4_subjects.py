from django.db import migrations


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
        ('resources', '0036_v4_citations'),
    ]

    operations = [
        migrations.RunPython(copy_subjects),
    ]
