from resources.models import FederalRegisterDocument, SupplementalContent
from file_manager.models import UploadedFile
from content_search.functions import add_to_index

from django.db import migrations

def populate_content(apps, schema_editor):
    supplemental_content = SupplementalContent.objects.all()
    fr_docs = FederalRegisterDocument.objects.all()
    up_files = UploadedFile.objects.all()

    for sc in supplemental_content:
        add_to_index(sc)
    
    for fr in fr_docs:
        add_to_index(fr)
    
    for up in up_files:
        add_to_index(up)



class Migration(migrations.Migration):

    dependencies = [
        ('content_search', '0002_add_vector'),
    ]

    operations = [
        migrations.RunPython(populate_content),
    ]
