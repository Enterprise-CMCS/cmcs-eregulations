from django.db import migrations, models, transaction
from django.db.models import Q


def update_ref_field_sort(apps, schema_editor):
    # Resave all Resource objects to trigger the pre-save hook for the ref fields
    AbstractResource = apps.get_model("resources", "AbstractResource")
    q_filter = Q(usc_citations__isnull=False) | Q(act_citations__isnull=False)
    pk = -1  # Start with the lowest pk to ensure we process all resources

    while True:
        with transaction.atomic():            
            # Process 100 resources at a time to avoid a statement timeout while maintaining atomicity
            resources = AbstractResource.objects.filter(Q(pk__gt=pk) & q_filter).order_by("pk")[:100]

            if not resources:
                break

            for resource in resources:
                pk = resource.pk
                resource.save()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('resources', '0007_create_citation_sort_field'),
    ]

    operations = [
        migrations.RunPython(update_ref_field_sort, reverse_code=migrations.RunPython.noop),
    ]
