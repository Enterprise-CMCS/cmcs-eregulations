#!/usr/bin/env python
import os


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    import django
    django.setup()

    from django.db import connection
    connection.ensure_connection()
    try:
        if not connection.is_usable():
            raise Exception("database is unreachable")
    except Exception as e:
        print(e)

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{os.environ.get('STAGE', '')}'")
        cursor.execute(f"DROP DATABASE {os.environ.get('STAGE', '')}")
    print(f"Database {os.environ.get('STAGE', '')} has been removed")
