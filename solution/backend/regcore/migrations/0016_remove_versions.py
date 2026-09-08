from django.db import migrations


def remove_versions(apps, schema_editor):
    Part = apps.get_model("regcore", "Part")
    latest_pks = Part.objects.order_by("title", "name", "-date").distinct("title", "name").values_list('pk', flat=True)

    if apps.is_installed("content_search"):
        IndexedRegulationText = apps.get_model("content_search", "IndexedRegulationText")
        indexed_text_pks = IndexedRegulationText.objects.exclude(part__pk__in=latest_pks).values_list("pk", flat=True)
        ContentIndex = apps.get_model("content_search", "ContentIndex")
        ContentIndex.objects.filter(reg_text__pk__in=indexed_text_pks).delete()
        IndexedRegulationText.objects.filter(pk__in=indexed_text_pks).delete()

    Part.objects.exclude(pk__in=latest_pks).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('regcore', '0015_move_parser_models_to_parsers'),
    ]

    operations = [
        migrations.RunPython(remove_versions),
    ]
