# Generated by Django 3.2.13 on 2022-06-30 16:18

from django.db import migrations


def convert_docket_number_to_list(apps, schema_editor):
    FederalRegisterDocument = apps.get_model("resources", "FederalRegisterDocument")
    for doc in FederalRegisterDocument.objects.all():
        if doc.docket_number_tmp is not None and doc.docket_number_tmp != "":
            doc.docket_numbers.append(doc.docket_number_tmp)
            doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0017_grouped_fr_docs'),
    ]

    operations = [
        migrations.RunPython(convert_docket_number_to_list),
        migrations.RemoveField(
            model_name='federalregisterdocument',
            name='docket_number_tmp',
        ),
    ]
