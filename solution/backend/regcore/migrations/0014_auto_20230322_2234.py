# Generated by Django 3.2.18 on 2023-03-22 22:34

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


def migrate_configuration(apps, schema_editor):
    PartConfiguration = apps.get_model("regcore", "PartConfiguration")
    TitleConfiguration = apps.get_model("regcore", "TitleConfiguration")
    ParserConfiguration = apps.get_model("regcore", "ParserConfiguration")

    parser_config = ParserConfiguration.objects.first()

    for i in TitleConfiguration.objects.all():
        for subchapter in [j.strip() for j in i.subchapters.split(",")]:
            if subchapter:
                PartConfiguration.objects.create(
                    title=i.title,
                    type="subchapter",
                    value=subchapter,
                    parser_config=parser_config,
                )

        for part in [j.strip() for j in i.parts.split(",")]:
            if part:
                PartConfiguration.objects.create(
                    title=i.title,
                    type="part",
                    value=part,
                    parser_config=parser_config,
                )


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0013_alter_part_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.IntegerField(help_text='The title of the regulations to parse, e.g. 42.')),
                ('type', models.CharField(choices=[('subchapter', 'Subchapter'), ('part', 'Part')], default='part', max_length=255)),
                ('value', models.CharField(help_text='A subchapter or part to parse. E.g., "IV-C" or "400".', max_length=255, validators=[django.core.validators.RegexValidator(message='Please enter a valid part or subchapter, e.g. "IV-C" or "400".', regex='^([A-Za-z]+-[A-Za-z]+)|(\\d+)$')])),
                ('upload_reg_text', models.BooleanField(default=True, help_text='Should the eCFR parser upload regulation text to eRegs?')),
                ('upload_locations', models.BooleanField(default=True, help_text='Should the parser process and upload section and subpart names for use in resource management?')),
                ('upload_fr_docs', models.BooleanField(default=True, help_text='Should the FR parser upload Federal Register Documents to eRegs?')),
                ('parser_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts', to='regcore.parserconfiguration')),
            ],
            options={
                'verbose_name': 'Part',
                'verbose_name_plural': 'Parts',
            },
        ),
        migrations.RunPython(migrate_configuration),
        migrations.DeleteModel(
            name='TitleConfiguration',
        ),
    ]
