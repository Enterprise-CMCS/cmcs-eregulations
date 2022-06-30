# Generated by Django 3.2.13 on 2022-06-30 15:10

import django_jsonform.models.fields
from django.db import migrations, models


def convert_docket_number_to_list(apps, schema_editor):
    FederalRegisterDocument = apps.get_model("resources", "FederalRegisterDocument")
    for doc in FederalRegisterDocument.objects.all():
        if doc.docket_number_tmp is not None and doc.docket_number_tmp != "":
            doc.docket_numbers.append(doc.docket_number_tmp)
            doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0016_v3_rewrite'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='federalregisterdocument',
            options={'ordering': ['-date', 'document_number', 'name', 'description'], 'verbose_name': 'Federal Register Document', 'verbose_name_plural': 'Federal Register Documents'},
        ),
        migrations.RenameField(
            model_name='federalregisterdocument',
            old_name='docket_number',
            new_name='docket_number_tmp',
        ),
        migrations.AddField(
            model_name='federalregisterdocument',
            name='docket_numbers',
            field=django_jsonform.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255, null=True), default=list, blank=True, size=None),
        ),
        migrations.RunPython(convert_docket_number_to_list),
        migrations.RemoveField(
            model_name='federalregisterdocument',
            name='docket_number_tmp',
        ),
    ]
