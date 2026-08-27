from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parsers", "0004_ecfrlauncherresult"),
    ]

    operations = [
        migrations.AddField(
            model_name="ecfrlauncherresult",
            name="failed_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="ecfrlauncherresult",
            name="queued_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="ecfrlauncherresult",
            name="skipped_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="ecfrlauncherresult",
            name="succeeded_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
