# Generated by Django 5.2.1 on 2025-06-09 10:58

import pgvector.django.vector
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content_search', '0007_enable_pgvector'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentindex',
            name='embedding',
            field=pgvector.django.vector.VectorField(blank=True, default=None, dimensions=512, null=True),
        ),
    ]
