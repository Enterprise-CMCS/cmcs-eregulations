from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parsers", "0007_alter_abstractparserresult_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="ecfrparserresult",
            name="invalidated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
