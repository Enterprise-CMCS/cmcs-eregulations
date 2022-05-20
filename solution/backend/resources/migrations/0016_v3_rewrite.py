# Generated by Django 3.2.12 on 2022-05-03 12:51

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


def exists(field):
    return field is not None and field != ""


def convert_old_supp_content(apps, schema_editor):
    TempSupplementalContent = apps.get_model("resources", "TempSupplementalContent")
    SupplementalContent = apps.get_model("resources", "SupplementalContent")
    FederalRegisterDocument = apps.get_model("resources", "FederalRegisterDocument")

    for old_content in TempSupplementalContent.objects.all():
        if exists(old_content.docket_number) or exists(old_content.document_number):
            # content is assumed to be a Federal Register document
            content = FederalRegisterDocument.objects.create(
                docket_number=old_content.docket_number,
                document_number=old_content.document_number,
            )
        else:
            # content is assumed to be normal Supplemental Content
            content = SupplementalContent.objects.create()
        
        # set common fields
        for field in ["created_at", "updated_at", "approved", "category", "name", "description", "url", "date"]:
            setattr(content, field, getattr(old_content, field))
        content.locations.add(*old_content.locations.all())
        content.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0015_supplementalcontent_document_number'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SubSubCategory',
        ),
        migrations.AlterModelOptions(
            name='abstractlocation',
            options={'ordering': ['title', 'part', 'section__section_id', 'subpart__subpart_id']},
        ),
        migrations.RemoveField(
            model_name='abstractcategory',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='abstractlocation',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='abstractsupplementalcontent',
            name='display_name',
        ),
        migrations.DeleteModel(
            name='SubjectGroup',
        ),
        migrations.CreateModel(
            name='AbstractResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved', models.BooleanField(default=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resources', to='resources.abstractcategory')),
                ('locations', models.ManyToManyField(blank=True, related_name='resources', to='resources.AbstractLocation')),
            ],
        ),
        migrations.RenameModel(
            old_name='SupplementalContent',
            new_name='TempSupplementalContent',
        ),
        migrations.CreateModel(
            name='FederalRegisterDocument',
            fields=[
                ('abstractresource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractresource')),
                ('name', models.CharField(blank=True, max_length=512, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('url', models.URLField(blank=True, max_length=512, null=True)),
                ('date', models.CharField(blank=True, help_text='Leave blank or enter one of: "YYYY", "YYYY-MM", or "YYYY-MM-DD".', max_length=10, null=True, validators=[django.core.validators.RegexValidator(message='Date field must be blank or of format "YYYY", "YYYY-MM", or "YYYY-MM-DD"! For example: 2021, 2021-01, or 2021-01-31.', regex='^\\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$')])),
                ('docket_number', models.CharField(blank=True, max_length=255, null=True)),
                ('document_number', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Federal Register Document',
                'verbose_name_plural': 'Federal Register Documents',
            },
            bases=('resources.abstractresource', models.Model),
        ),
        migrations.CreateModel(
            name='SupplementalContent',
            fields=[
                ('abstractresource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.abstractresource')),
                ('name', models.CharField(blank=True, max_length=512, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('url', models.URLField(blank=True, max_length=512, null=True)),
                ('date', models.CharField(blank=True, help_text='Leave blank or enter one of: "YYYY", "YYYY-MM", or "YYYY-MM-DD".', max_length=10, null=True, validators=[django.core.validators.RegexValidator(message='Date field must be blank or of format "YYYY", "YYYY-MM", or "YYYY-MM-DD"! For example: 2021, 2021-01, or 2021-01-31.', regex='^\\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$')])),
            ],
            options={
                'verbose_name': 'Supplemental Content',
                'verbose_name_plural': 'Supplemental Content',
            },
            bases=('resources.abstractresource', models.Model),
        ),
        migrations.RunPython(convert_old_supp_content),
        migrations.DeleteModel(
            name='TempSupplementalContent',
        ),
        migrations.DeleteModel(
            name='AbstractSupplementalContent',
        ),
        migrations.AddField(
            model_name='federalregisterdocument',
            name='internal_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supplementalcontent',
            name='internal_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='FederalRegisterCategoryLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the category as sent from the Federal Register parser.', max_length=512, unique=True)),
                ('category', models.ForeignKey(help_text='The eRegs category to translate a Federal Register category into.', on_delete=django.db.models.deletion.CASCADE, related_name='federal_register_category_link', to='resources.abstractcategory')),
            ],
            options={
                'verbose_name': 'Federal Register Category Link',
                'verbose_name_plural': 'Federal Register Category Links',
            },
        ),
        migrations.AlterModelOptions(
            name='abstractcategory',
            options={'ordering': ['order', 'name']},
        ),
        migrations.AlterModelOptions(
            name='federalregisterdocument',
            options={'ordering': ['-date', 'document_number', 'docket_number', 'name', 'description'], 'verbose_name': 'Federal Register Document', 'verbose_name_plural': 'Federal Register Documents'},
        ),
        migrations.AlterModelOptions(
            name='supplementalcontent',
            options={'ordering': ['-date', 'name', 'description'], 'verbose_name': 'Supplemental Content', 'verbose_name_plural': 'Supplemental Content'},
        ),
    ]
