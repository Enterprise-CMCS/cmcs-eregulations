# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0003_mptt_copy_children'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='regulation',
            name='children',
        ),
    ]
