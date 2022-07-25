# Generated by Django 3.2.11 on 2022-01-07 15:34

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


def create_default_parser_config(apps, schema_editor):
    ParserConfiguration = apps.get_model("regcore", "ParserConfiguration")
    TitleConfiguration = apps.get_model("regcore", "TitleConfiguration")

    if len(ParserConfiguration.objects.all()) < 1:
        parser_config = ParserConfiguration.objects.create()
        TitleConfiguration.objects.create(
            title=42,
            subchapters="IV-C",
            parts="400, 457, 460",
            parser_config=parser_config,
        )
        TitleConfiguration.objects.create(
            title=45,
            parts="75, 95, 155",
            parser_config=parser_config,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParserConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workers', models.IntegerField(default=3, help_text='The number of worker threads used to parse regulations.', validators=[django.core.validators.MinValueValidator(limit_value=1, message='Number of workers must be at least 1!')])),
                ('attempts', models.IntegerField(default=3, help_text='Number of times to retry parsing if it fails to complete.', validators=[django.core.validators.MinValueValidator(limit_value=1, message='Number of attempts must be at least 1!')])),
                ('loglevel', models.CharField(choices=[('fatal', 'Fatal'), ('error', 'Error'), ('warn', 'Warning'), ('info', 'Info'), ('debug', 'Debug'), ('trace', 'Trace')], default='warn', help_text="Specifies the level of detail contained in the parser's logs.", max_length=5)),
                ('upload_supplemental_locations', models.BooleanField(default=True, help_text='Should the parser process and upload section and subpart names for use in supplemental content management?')),
                ('log_parse_errors', models.BooleanField(default=False, help_text='Should the parser log errors encountered while processing the raw XML data from eCFR?')),
                ('skip_versions', models.BooleanField(default=True, help_text='Should the parser skip processing versions of parts that have been previously processed?')),
            ],
            options={
                'verbose_name': 'Parser Configuration',
            },
        ),
        migrations.CreateModel(
            name='TitleConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.IntegerField(help_text='The title of the regulations to parse, e.g. 42.', unique=True)),
                ('subchapters', models.TextField(blank=True, help_text='A comma-separated list of subchapters to parse. All parts within the listed subchapters will be included. E.g., "IV-C, IV-D, IV-F" or simply "IV-C".', validators=[django.core.validators.RegexValidator(message='Please enter a comma-separated list of subchapters, e.g. "IV-C, IV-D, IV-F" or "IV-C".', regex='^([A-Za-z]+-[A-Za-z]+)(,\\s*([A-Za-z]+-[A-Za-z]+))*$')])),
                ('parts', models.TextField(blank=True, help_text='A comma-separated list of individual parts to parse if you do not wish to include the entire subchapter. E.g., "400, 457, 460" or simply "400".', validators=[django.core.validators.RegexValidator(message='Please enter a comma-separated list of part numbers, e.g. "400, 457, 460" or "400".', regex='^(\\d+)(,\\s*\\d+)*$')])),
                ('parser_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='titles', to='regcore.parserconfiguration')),
            ],
            options={
                'verbose_name': 'Title',
                'verbose_name_plural': 'Titles',
            },
        ),
        migrations.RunPython(create_default_parser_config),
    ]
