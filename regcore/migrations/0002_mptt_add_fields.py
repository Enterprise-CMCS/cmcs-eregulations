# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields

from regcore.fields import CompressedJSONField


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='regulation',
            name='level',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='regulation',
            name='lft',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='regulation',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, to='regcore.Regulation', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='regulation',
            name='rght',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='regulation',
            name='tree_id',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='regulation',
            name='id',
            field=models.TextField(serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='regulation',
            name='children',
            field=CompressedJSONField(null=True, blank=True),
        ),
    ]
