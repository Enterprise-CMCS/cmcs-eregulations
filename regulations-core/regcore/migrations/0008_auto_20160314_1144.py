# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0007_auto_20160314_1135'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='layer',
            unique_together=set([('name', 'reference')]),
        ),
        migrations.AlterIndexTogether(
            name='layer',
            index_together=set([('name', 'reference')]),
        ),
        migrations.AlterField(
            model_name='layer',
            name='label',
            field=models.SlugField(max_length=200, default='')),
        migrations.RemoveField(
            model_name='layer',
            name='label',
        ),
        migrations.AlterField(
            model_name='layer',
            name='version',
            field=models.SlugField(max_length=20, default='')),
        migrations.RemoveField(
            model_name='layer',
            name='version',
        ),
    ]
