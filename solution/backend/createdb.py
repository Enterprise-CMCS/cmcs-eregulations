#!/usr/bin/env python
import os


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    import django
    django.setup()

    print(f"{os.environ.get('STAGE')}")
    print(f"{os.environ.get('DB_USER')}")
    print(f"{os.environ.get('DB_NAME')}")
    from cmcs_regulations import settings
    print(f"{settings.DATABASES}")


    from django.db import connection, ProgrammingError
    connection.ensure_connection()
    if not connection.is_usable():
        raise Exception("database is unreachable")

    #try:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'main'"
        )
        cursor.execute(
            f"CREATE DATABASE {os.environ.get('STAGE')} OWNER {os.environ.get('DB_USER')}"
        )
    # except ProgrammingError:
    #     # The next step will tell us if this is a problem.
    #     pass
