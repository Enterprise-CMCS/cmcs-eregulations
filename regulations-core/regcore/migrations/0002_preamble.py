# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import regcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preamble',
            fields=[
                ('document_number', models.SlugField(max_length=20, serialize=False, primary_key=True)),
                ('data', regcore.fields.CompressedJSONField()),
            ],
        ),
    ]
