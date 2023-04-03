from django.db import migrations
from regcore.models import Part


def update_part(apps, schema_editor):
    parts = Part.objects.all()
    for part in parts:
        part = part
        part.save()

class Migration(migrations.Migration):

    dependencies = [
        ('search', '0006_delete_searchindex'),
    ]

    operations = [
        migrations.RunPython(update_part),
    ]
