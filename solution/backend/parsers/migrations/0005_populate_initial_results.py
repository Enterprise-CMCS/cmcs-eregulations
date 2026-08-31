from django.db import migrations


def populate_initial_results(apps, schema_editor):
    EcfrParserResult = apps.get_model("parsers", "EcfrParserResult")
    EcfrLauncherResult = apps.get_model("parsers", "EcfrLauncherResult")

    latest_timestamp = (
        EcfrParserResult.objects.order_by("-timestamp").first().timestamp
        if EcfrParserResult.objects.exists()
        else None
    )

    if latest_timestamp:
        launcher_result = EcfrLauncherResult.objects.create(
            success=True,
            log="Post-migration: This record was created to preserve the latest successful parser run.",
        )
        EcfrLauncherResult.objects.all().update(timestamp=latest_timestamp)

        for parser_result in EcfrParserResult.objects.all():
            parser_result.launcher_result = launcher_result
            parser_result.status_updated_at = parser_result.timestamp
            parser_result.save()


class Migration(migrations.Migration):

    dependencies = [
        ("parsers", "0004_ecfrlauncherresult"),
    ]

    operations = [
        migrations.RunPython(populate_initial_results, reverse_code=migrations.RunPython.noop),
    ]
