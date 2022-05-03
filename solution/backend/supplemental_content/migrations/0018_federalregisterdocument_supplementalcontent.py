# Generated by Django 3.2.12 on 2022-05-03 13:44

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supplemental_content', '0017_rename_supplementalcontent_tempsupplementalcontent'),
    ]

    operations = [
        migrations.CreateModel(
            name='FederalRegisterDocument',
            fields=[
                ('abstractsupplementalcontent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supplemental_content.abstractsupplementalcontent')),
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
            bases=('supplemental_content.abstractsupplementalcontent', models.Model),
        ),
        migrations.CreateModel(
            name='SupplementalContent',
            fields=[
                ('abstractsupplementalcontent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supplemental_content.abstractsupplementalcontent')),
                ('name', models.CharField(blank=True, max_length=512, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('url', models.URLField(blank=True, max_length=512, null=True)),
                ('date', models.CharField(blank=True, help_text='Leave blank or enter one of: "YYYY", "YYYY-MM", or "YYYY-MM-DD".', max_length=10, null=True, validators=[django.core.validators.RegexValidator(message='Date field must be blank or of format "YYYY", "YYYY-MM", or "YYYY-MM-DD"! For example: 2021, 2021-01, or 2021-01-31.', regex='^\\d{4}((-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]))|(-(0[1-9]|1[0-2])))?$')])),
            ],
            options={
                'verbose_name': 'Supplemental Content',
                'verbose_name_plural': 'Supplemental Content',
            },
            bases=('supplemental_content.abstractsupplementalcontent', models.Model),
        ),
    ]
