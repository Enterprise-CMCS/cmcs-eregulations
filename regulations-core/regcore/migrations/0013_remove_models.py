# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0012_migrate_documents'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Preamble',
        ),
        migrations.AlterUniqueTogether(
            name='regulation',
            unique_together=set([]),
        ),
        migrations.AlterIndexTogether(
            name='regulation',
            index_together=set([]),
        ),
        migrations.RemoveField(
            model_name='regulation',
            name='parent',
        ),
        migrations.DeleteModel(
            name='Regulation',
        ),
    ]
