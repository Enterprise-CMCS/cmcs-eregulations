# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forward(apps, schema_editor):
    schema_editor.execute("""
        UPDATE regcore_layer SET doc_id=REPLACE(doc_id, ':', '/')
        WHERE doc_type='cfr';
    """)


def backward(apps, schema_editor):
    schema_editor.execute("""
        UPDATE regcore_layer SET doc_id=REPLACE(doc_id, '/', ':')
        WHERE doc_type='cfr';
    """)


class Migration(migrations.Migration):
    """Convert doc_ids like 11_22:33-44-aa into 11_22/33-44-aa"""

    dependencies = [
        ('regcore', '0009_auto_20160322_1646'),
    ]

    operations = [
        migrations.RunPython(forward, backward)
    ]
