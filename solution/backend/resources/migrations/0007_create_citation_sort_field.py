# Generated by Django 5.1.7 on 2025-05-06 13:22

from django.db import migrations, models, transaction
from django.db.models import Q


def populate_section_child_id(apps, schema_editor):
    Section = apps.get_model('resources', 'Section')
    q_filter = Q(child_id="")
    while Section.objects.filter(q_filter).exists():
        with transaction.atomic():
            for section in Section.objects.filter(q_filter)[:100]:
                section.child_id = f"{section.section_id:012d}"
                section.save()


def populate_subpart_child_id(apps, schema_editor):
    Subpart = apps.get_model('resources', 'Subpart')
    q_filter = Q(child_id="")
    while Subpart.objects.filter(q_filter).exists():
        with transaction.atomic():
            for subpart in Subpart.objects.filter(q_filter)[:100]:
                subpart.child_id = subpart.subpart_id
                subpart.save()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('resources', '0006_recompute_groups'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='abstractcitation',
            options={'ordering': ['title', 'part', 'child_id']},
        ),
        migrations.AddField(
            model_name='abstractcitation',
            name='child_id',
            field=models.CharField(default='', max_length=12),
            preserve_default=False,
        ),
        migrations.RunPython(populate_section_child_id, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(populate_subpart_child_id, reverse_code=migrations.RunPython.noop),
    ]
