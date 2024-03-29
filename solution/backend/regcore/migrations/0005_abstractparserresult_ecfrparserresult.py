# Generated by Django 3.2.12 on 2022-04-21 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0004_part_depth'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractParserResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('title', models.IntegerField()),
                ('subchapters', models.TextField(blank=True)),
                ('parts', models.TextField(blank=True)),
                ('workers', models.IntegerField()),
                ('attempts', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ECFRParserResult',
            fields=[
                ('abstractparserresult_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='regcore.abstractparserresult')),
                ('totalVersions', models.IntegerField()),
                ('skippedVersions', models.IntegerField()),
                ('errors', models.IntegerField()),
            ],
            bases=('regcore.abstractparserresult',),
        ),
    ]
