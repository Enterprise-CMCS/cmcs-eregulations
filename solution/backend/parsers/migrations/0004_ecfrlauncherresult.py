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
    ]
