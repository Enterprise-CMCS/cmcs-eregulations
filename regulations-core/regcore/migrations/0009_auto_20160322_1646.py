# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0008_auto_20160314_1144'),
    ]

    operations = [
        migrations.RenameField(
            model_name='layer',
            old_name='reference',
            new_name='doc_id',
        ),
        migrations.AddField(
            model_name='layer',
            name='doc_type',
            field=models.SlugField(default='cfr', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='layer',
            unique_together=set([('name', 'doc_type', 'doc_id')]),
        ),
        migrations.AlterIndexTogether(
            name='layer',
            index_together=set([('name', 'doc_type', 'doc_id')]),
        ),
    ]
