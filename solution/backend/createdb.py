#!/usr/bin/env python
import os


def handler(event, context):
    TIMEOUT_MINUTES = 3

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")

    import django
    django.setup()

    from django.db import ProgrammingError, connection

    connection.ensure_connection()
    if not connection.is_usable():
        raise Exception("database is unreachable")

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SET LOCAL statement_timeout TO {TIMEOUT_MINUTES * 60000};")
            cursor.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname = 'eregs'"
            )
            cursor.execute(
                f"CREATE DATABASE {os.environ.get('DB_NAME')} WITH TEMPLATE eregs "
                f"STRATEGY FILE_COPY OWNER {os.environ.get('DB_USER')}"
            )
    except ProgrammingError:
        # This is raised if the database already exists
        pass
