# Generated by Django 3.2.13 on 2022-06-30 16:18

import django_jsonform.models.fields
from django.db import migrations, models
import django.db.models.deletion


def convert_docket_number_to_list(apps, schema_editor):
    FederalRegisterDocument = apps.get_model("resources", "FederalRegisterDocument")
    for doc in FederalRegisterDocument.objects.all():
        if doc.docket_number_tmp is not None and doc.docket_number_tmp != "":
            nums = doc.docket_number_tmp.split(",")
            for num in nums:
                doc.docket_numbers.append(num.strip())
            doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0017_create_docket_array'),
    ]

    operations = [
        migrations.RunPython(convert_docket_number_to_list),
        migrations.RemoveField(
            model_name='federalregisterdocument',
            name='docket_number_tmp',
        ),
        migrations.CreateModel(
            name='FederalRegisterDocumentGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('docket_number_prefixes', django_jsonform.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255, null=True), blank=True, default=list, help_text='Common prefixes to use when grouping Federal Register Documents, e.g. "CMS-1234-" to match any docket number starting with that string.', size=None)),
            ],
            options={
                'verbose_name': 'Federal Register Doc Group',
                'verbose_name_plural': 'Federal Register Doc Groups',
            },
        ),
        migrations.AddField(
            model_name='federalregisterdocument',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='documents', to='resources.federalregisterdocumentgroup'),
        ),
    ]
