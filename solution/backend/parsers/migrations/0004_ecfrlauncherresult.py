from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parsers", "0003_alter_ecfrparserresult_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EcfrLauncherResult",
            fields=[
                (
                    "abstractparserresult_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=models.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="parsers.abstractparserresult",
                    ),
                ),
            ],
            options={
                "verbose_name": "eCFR Launcher Result",
                "verbose_name_plural": "eCFR Launcher Results",
            },
            bases=("parsers.abstractparserresult",),
        ),
        migrations.AddField(
            model_name="ecfrparserresult",
            name="launcher_result",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.CASCADE,
                related_name="part_results",
                to="parsers.ecfrlauncherresult",
            ),
        ),
        migrations.AddField(
            model_name="ecfrparserresult",
            name="status",
            field=models.CharField(
                choices=[
                    ("queued", "Queued"),
                    ("skipped", "Skipped"),
                    ("succeeded", "Succeeded"),
                    ("failed", "Failed"),
                ],
                default="succeeded",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="ecfrparserresult",
            name="status_updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="ecfrparserresult",
            name="date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name="ecfrparserresult",
            constraint=models.UniqueConstraint(
                fields=("launcher_result", "title", "part", "date"),
                name="unique_ecfr_part_result_per_launcher_run",
            ),
        ),
    ]
