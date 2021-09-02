# Generated by Django 3.2.5 on 2021-08-31 16:12

import django.core.validators
from django.db import migrations, models
from django.db.migrations.operations.fields import RenameField


def migrate_dates(apps, schema_editor):
    SupplementaryContent = apps.get_model("supplementary_content", "SupplementaryContent")
    for content in SupplementaryContent.objects.all():
        if content.old_date is not None:
            # Note: Prior to this migration, year month and date must all exist or date would be None.
            year = content.old_date.year
            month = content.old_date.month
            day = content.old_date.day
            content.date = f'{year}-{month:02d}-{day:02d}'
        content.save()


class Migration(migrations.Migration):

    dependencies = [
        ('supplementary_content', '0006_alter_regulationsection_supplementary_content'),
    ]

    operations = [
        migrations.RenameField(
            model_name='supplementarycontent',
            old_name='date',
            new_name='old_date',
        ),
        migrations.AddField(
            model_name='supplementarycontent',
            name='date',
            field=models.CharField(blank=True, max_length=10, null=True, validators=[
                django.core.validators.RegexValidator(
                    message='Date must be of format "YYYY", "YYYY-MM", or "YYYY-MM-DD"!',
                    regex='^\\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$'
                )
            ]),
        ),
        migrations.RunPython(migrate_dates),
        migrations.RemoveField(
            model_name='supplementarycontent',
            name='old_date',
        ),
    ]
