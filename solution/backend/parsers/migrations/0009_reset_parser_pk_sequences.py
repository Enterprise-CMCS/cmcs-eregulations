from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("parsers", "0008_ecfrparserresult_invalidated_at"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            SELECT setval(
                pg_get_serial_sequence('parsers_parserconfiguration', 'id'),
                COALESCE(MAX(id), 1),
                MAX(id) IS NOT NULL
            )
            FROM parsers_parserconfiguration;

            SELECT setval(
                pg_get_serial_sequence('parsers_partconfiguration', 'id'),
                COALESCE(MAX(id), 1),
                MAX(id) IS NOT NULL
            )
            FROM parsers_partconfiguration;

            SELECT setval(
                pg_get_serial_sequence('parsers_abstractparserresult', 'id'),
                COALESCE(MAX(id), 1),
                MAX(id) IS NOT NULL
            )
            FROM parsers_abstractparserresult;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
