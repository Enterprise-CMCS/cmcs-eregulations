# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0013_remove_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='node_type',
            field=models.SlugField(max_length=30),
        ),
    ]
