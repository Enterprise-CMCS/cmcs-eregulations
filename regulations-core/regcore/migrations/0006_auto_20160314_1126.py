# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0005_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='layer',
            name='reference',
            field=models.SlugField(default='', max_length=250),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='regulation',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', blank=True, to='regcore.Regulation', null=True, on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='layer',
            unique_together=set()
        ),
        migrations.AlterIndexTogether(
            name='layer',
            index_together=set()
        ),
    ]
