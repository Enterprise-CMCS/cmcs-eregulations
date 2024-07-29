# Generated by Django 5.0.4 on 2024-07-23 15:26

from django.db import migrations


def populate_config(apps, schema_editor):
    PublicCategory = apps.get_model("resources", "PublicCategory")
    PublicSubCategory = apps.get_model("resources", "PublicSubCategory")
    ResourcesConfiguration = apps.get_model("resources", "ResourcesConfiguration")
    
    config = (ResourcesConfiguration.objects.create()
                if len(ResourcesConfiguration.objects.all()) < 1
                else ResourcesConfiguration.objects.first())

    if not config.fr_link_category:
        try:
            category = PublicCategory.objects.filter(name__in=["Federal Register Docs", "Federal Register Links"]).first()
        except PublicCategory.DoesNotExist:
            try:
                category = PublicSubCategory.objects.filter(name__in=["Federal Register Docs", "Federal Register Links"]).first()
            except PublicSubCategory.DoesNotExist:
                category = PublicCategory.objects.create(name="Federal Register Links")
        config.fr_link_category = category
        config.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_to_0052_squashed'),
    ]

    operations = [
        migrations.RunPython(populate_config),
    ]