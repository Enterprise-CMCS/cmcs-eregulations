from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("regcore", "0014_auto_20230322_2234"),
        ("parsers", "0002_move_parser_data_from_regcore"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ECFRParserResult",
        ),
        migrations.DeleteModel(
            name="PartConfiguration",
        ),
        migrations.DeleteModel(
            name="ParserConfiguration",
        ),
        migrations.DeleteModel(
            name="AbstractParserResult",
        ),
    ]
