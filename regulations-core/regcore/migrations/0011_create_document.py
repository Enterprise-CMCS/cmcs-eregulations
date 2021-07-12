# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0010_auto_20160322_1704'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.TextField(serialize=False, primary_key=True)),
                ('doc_type', models.SlugField(max_length=20)),
                ('version', models.SlugField(max_length=20, null=True, blank=True)),
                ('label_string', models.SlugField(max_length=200)),
                ('text', models.TextField()),
                ('title', models.TextField(blank=True)),
                ('node_type', models.SlugField(max_length=10)),
                ('root', models.BooleanField(default=False, db_index=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='regcore.Document', null=True, on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together=set([('doc_type', 'version', 'label_string')]),
        ),
        migrations.AlterIndexTogether(
            name='document',
            index_together=set([('doc_type', 'version', 'label_string')]),
        ),
    ]
