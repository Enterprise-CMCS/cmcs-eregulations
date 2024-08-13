# Created by Caleb Godwin on 2024-08-12
# Blanks the extract_url field for all non-FR-link resources

import django.db.models.deletion
from django.db import migrations, models


def blank_extract_url(apps, schema_editor):
    AbstractResource = apps.get_model("resources", "AbstractResource")
    AbstractResource.objects.filter(abstractpublicresource__federalregisterlink__isnull=True).update(extract_url="")


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0004_resourcesconfiguration_auto_extract_and_more'),
    ]

    operations = [
        migrations.RunPython(blank_extract_url, reverse_code=migrations.RunPython.noop),
    ]
