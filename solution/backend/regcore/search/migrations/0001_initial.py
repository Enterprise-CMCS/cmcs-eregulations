# Generated by Django 3.2.5 on 2021-07-12 18:17

import django.contrib.postgres.fields
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('regcore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchIndex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=32)),
                ('label', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=32), size=None)),
                ('content', models.TextField()),
                ('parent', models.JSONField(null=True)),
                ('search_vector', django.contrib.postgres.search.SearchVectorField()),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='regcore.part')),
            ],
            options={
                'unique_together': {('label', 'part')},
            },
        ),
    ]
