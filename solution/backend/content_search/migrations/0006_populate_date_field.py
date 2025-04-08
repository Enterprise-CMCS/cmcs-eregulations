from django.db import migrations, models, transaction
from django.db.models import Q


def populate_date(apps, schema_editor):
    ContentIndex = apps.get_model('content_search', 'ContentIndex')
    q_filter = Q(resource__isnull=False) & ~Q(resource__date="") & Q(date__isnull=True)
    while ContentIndex.objects.filter(q_filter).exists():
        with transaction.atomic():
            for index in ContentIndex.objects.filter(q_filter)[:100]:
                index.date = index.resource.date or None
                index.save()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('content_search', '0005_contentindex_date'),
    ]

    operations = [
        migrations.RunPython(populate_date, reverse_code=migrations.RunPython.noop),
    ]
