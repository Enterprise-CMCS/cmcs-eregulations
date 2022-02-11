# Generated by Django 3.2.12 on 2022-02-11 11:39

from django.db import migrations


# Re-save locations to properly generate display_name field
# This didn't work in the previous migration because the "get_model" func reconstructs models from migrations, and custom save hooks are not included in that.
def resave_locations(apps, schema_editor):
    try:
        from supplemental_content.models import AbstractLocation
        locations = AbstractLocation.objects.all()
        for location in locations:
            location.save()
    except: # Primarily ImportError but safer to catch everything
        pass # Skip in case model is changed, renamed, or deleted in the future


class Migration(migrations.Migration):

    dependencies = [
        ('supplemental_content', '0010_abstractlocation_display_name'),
    ]

    operations = [
        migrations.RunPython(resave_locations),
    ]
