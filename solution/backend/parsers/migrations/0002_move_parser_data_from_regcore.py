from django.db import migrations


def move_parser_data_from_regcore(apps, schema_editor):
    RegcoreParserConfiguration = apps.get_model("regcore", "ParserConfiguration")
    RegcorePartConfiguration = apps.get_model("regcore", "PartConfiguration")
    RegcoreEcfrParserResult = apps.get_model("regcore", "ECFRParserResult")

    ParsersParserConfiguration = apps.get_model("parsers", "ParserConfiguration")
    ParsersPartConfiguration = apps.get_model("parsers", "PartConfiguration")
    ParsersEcfrParserResult = apps.get_model("parsers", "ECFRParserResult")

    for source in RegcoreParserConfiguration.objects.all().order_by("pk"):
        ParsersParserConfiguration.objects.update_or_create(
            pk=source.pk,
            defaults={
                "workers": source.workers,
                "retries": source.retries,
                "loglevel": source.loglevel,
                "upload_supplemental_locations": source.upload_supplemental_locations,
                "log_parse_errors": source.log_parse_errors,
                "skip_reg_versions": source.skip_reg_versions,
                "skip_fr_documents": source.skip_fr_documents,
            },
        )

    for source in RegcorePartConfiguration.objects.all().order_by("pk"):
        ParsersPartConfiguration.objects.update_or_create(
            pk=source.pk,
            defaults={
                "title": source.title,
                "type": source.type,
                "value": source.value,
                "upload_reg_text": source.upload_reg_text,
                "upload_locations": source.upload_locations,
                "upload_fr_docs": source.upload_fr_docs,
                "parser_config_id": source.parser_config_id,
            },
        )

    for source in RegcoreEcfrParserResult.objects.all().order_by("pk"):
        ParsersEcfrParserResult.objects.update_or_create(
            pk=source.pk,
            defaults={
                "start": source.start,
                "end": source.end,
                "title": source.title,
                "subchapters": source.subchapters,
                "parts": source.parts,
                "workers": source.workers,
                "totalVersions": source.totalVersions,
                "skippedVersions": source.skippedVersions,
                "errors": source.errors,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("parsers", "0001_initial"),
        ("regcore", "0014_auto_20230322_2234"),
    ]

    operations = [
        migrations.RunPython(move_parser_data_from_regcore, migrations.RunPython.noop),
    ]
