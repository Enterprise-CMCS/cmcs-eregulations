#!/usr/bin/env python
import os

import django
from django.db import connections
from django.db.utils import ProgrammingError


TIMEOUT_MINUTES = 3


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    django.setup()

    try:
        connection = connections["postgres"]
        connection.connect()
        connection.ensure_connection()
        if not connection.is_usable():
            raise Exception("database connection is not usable")
    except Exception as e:
        raise Exception(f"Failed to connect to the database: {str(e)}")

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
            print(f"Database {os.environ.get('DB_NAME')} has been created")
    except ProgrammingError:
        print("Database was not created, most likely because it already exists")
