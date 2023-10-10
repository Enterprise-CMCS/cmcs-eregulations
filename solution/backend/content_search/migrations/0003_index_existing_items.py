from django.db import migrations

from file_manager.models import UploadedFile
from resources.models import SupplementalContent, FederalRegisterDocument


def update_content(apps, schema_editor):
    sup_con = SupplementalContent.objects.all()
    for sup in sup_con:
        sup = sup
        sup.save()
    fr_doc = FederalRegisterDocument.objects.all()
    for fr in fr_doc:
        fr = fr
        fr.save()
    uploaded_file = UploadedFile.objects.all()
    for up in uploaded_file:
        up = up
        up.save()


class Migration(migrations.Migration):

    dependencies = [
        ('content_search', '0002_add_vector'),
    ]

    operations = [
        migrations.RunPython(update_content),
    ]
