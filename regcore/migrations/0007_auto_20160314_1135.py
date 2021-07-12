# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def gen_layer_reference(apps, schema_editor):
    """We'll combine two previously distinct fields to generalize the layers
    interface"""
    schema_editor.execute(
        "UPDATE regcore_layer SET reference=version||':'||label")


def split_layer_reference(apps, schema_editor):
    """Reverse of above"""
    Layer = apps.get_model("regcore", "Layer")
    for layer in Layer.objects.filter(reference__contains=':').iterator():
        layer.version, layer.label = layer.reference.split(':')
        layer.reference = ''
        layer.save()


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0006_auto_20160314_1126'),
    ]

    operations = [
        migrations.RunPython(gen_layer_reference, split_layer_reference)
    ]
