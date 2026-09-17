from django.db import migrations

BATCH_SIZE = 25


def remove_versions(apps, schema_editor):
    Part = apps.get_model("regcore", "Part")
    latest_pks = Part.objects.order_by("title", "name", "-date").distinct("title", "name").values_list("pk", flat=True)

    IndexedRegulationText = None
    ContentIndex = None

    if apps.is_installed("content_search"):
        IndexedRegulationText = apps.get_model("content_search", "IndexedRegulationText")
        ContentIndex = apps.get_model("content_search", "ContentIndex")

    while True:
        stale_part_ids = list(Part.objects.exclude(pk__in=latest_pks).order_by("pk").values_list("pk", flat=True)[:BATCH_SIZE])
        if not stale_part_ids:
            break

        if IndexedRegulationText and ContentIndex:
            while True:
                indexed_text_pks = list(
                    IndexedRegulationText.objects.filter(
                        part__pk__in=stale_part_ids
                    ).order_by("pk").values_list("pk", flat=True)[:BATCH_SIZE]
                )

                if not indexed_text_pks:
                    break

                ContentIndex.objects.filter(reg_text__pk__in=indexed_text_pks).delete()
                IndexedRegulationText.objects.filter(pk__in=indexed_text_pks).delete()

        Part.objects.filter(pk__in=stale_part_ids).delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('regcore', '0015_move_parser_models_to_parsers'),
    ]

    operations = [
        migrations.RunPython(remove_versions),
    ]
