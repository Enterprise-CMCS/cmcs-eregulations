#!/usr/bin/env python
import os


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")

    import django
    django.setup()

    from django.db import connection

    connection.ensure_connection()
    if not connection.is_usable():
        raise Exception("database is unreachable")

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'eregs'"
        )
    with connection.cursor() as cursor:
        cursor.execute(
            f"CREATE DATABASE {os.environ.get('STAGE')} WITH TEMPLATE eregs OWNER {os.environ.get('DB_USER')}"
        )
