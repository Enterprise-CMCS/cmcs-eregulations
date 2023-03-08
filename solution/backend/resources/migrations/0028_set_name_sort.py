from django.db import migrations
import resources.models
import re

def naturalize(string):
    def naturalize_int_match(match):
        return '%08d' % (int(match.group(0)),)
    if string:
        string = string.lower()
        string = string.strip()
        string = re.sub(r'\d+', naturalize_int_match, string)
        string = string[:50]

    return string

def add_default_name_sort(apps, schema_editor):
    SupplementalContent = apps.get_model("resources", "SupplementalContent")
    FederalRegisterDocument = apps.get_model("resources", "FederalRegisterDocument")

    for sup in SupplementalContent.objects.all():
        sup.name_sort = naturalize(sup.name)
        sup.description_sort = naturalize(sup.description)
        sup.save()

    for doc in FederalRegisterDocument.objects.all():
        doc.name_sort = naturalize(doc.name)
        doc.description_sort = naturalize(doc.description)
        doc.save()

class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0027_auto_20230308_0918'),
    ]

    operations = [
        migrations.RunPython(add_default_name_sort),
    ]
