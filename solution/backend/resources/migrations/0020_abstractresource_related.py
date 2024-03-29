# Generated by Django 3.2.13 on 2022-07-26 14:59

from django.db import migrations, models


def initial_set_related_resources(apps, schema_editor):
    FederalRegisterDocument = apps.get_model("resources", "FederalRegisterDocument")
    FederalRegisterDocumentGroup = apps.get_model("resources", "FederalRegisterDocumentGroup")

    for group in FederalRegisterDocumentGroup.objects.all():
        for doc in FederalRegisterDocument.objects.filter(group=group.id):
            doc.related_resources.set(group.documents.exclude(id=doc.id).order_by("-date"))
            doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0019_auto_group_fr_docs'),
    ]

    operations = [
        migrations.AddField(
            model_name='abstractresource',
            name='related_resources',
            field=models.ManyToManyField(blank=True, to='resources.AbstractResource'),
        ),
        migrations.RunPython(initial_set_related_resources),
    ]
