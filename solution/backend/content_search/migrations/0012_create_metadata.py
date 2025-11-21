from django.db import migrations, models, transaction
from django.db.models import Q


def create_resource_metadata(apps, schema_editor):
    ResourceMetadata = apps.get_model('content_search', 'ResourceMetadata')
    ContentIndex = apps.get_model('content_search', 'ContentIndex')
    pk = -1  # Start with the lowest pk to ensure we process all indices

    while True:
        with transaction.atomic():
            # Process 1000 indices at a time to avoid a statement timeout while maintaining atomicity
            indices = ContentIndex.objects.filter(Q(pk__gt=pk) & Q(resource__isnull=False)).order_by("pk")[:100]

            if not indices:
                break

            objects = ResourceMetadata.objects.bulk_create([ResourceMetadata(
                resource=index.resource,
                name=index.name,
                date=index.date,
                summary=index.summary,
                rank_a_string=index.rank_a_string,
                rank_b_string=index.rank_b_string,
                rank_c_string=index.rank_c_string,
                rank_d_string=index.rank_d_string,
                detected_file_type=getattr(index.resource, 'detected_file_type', ''),
                extraction_error=getattr(index.resource, 'extraction_error', ''),
            ) for index in indices])

            # Prepare a list of ContentIndex objects to update their resource_metadata field
            for obj, index in zip(objects, list(indices)):
                index.resource_metadata = obj
            ContentIndex.objects.bulk_update(indices, ['resource_metadata'])

            pk = indices.last().pk


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('content_search', '0011_enable_chunking'),
    ]

    operations = [
        migrations.RunPython(create_resource_metadata, reverse_code=migrations.RunPython.noop),
    ]
