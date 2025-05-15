from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):
    dependencies = [
        ('content_search', '0006_populate_date_field'),
    ]

    operations = [
        VectorExtension(),
    ]
