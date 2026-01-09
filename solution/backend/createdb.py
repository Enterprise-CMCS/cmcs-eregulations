#!/usr/bin/env python
import os

import django
from django.db import connections
from django.db.utils import ProgrammingError

from secret_manager import get_username

TIMEOUT_MINUTES = 15


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    django.setup()

    db_user = get_username("DB_SECRET", environment_fallback="DB_USER", default="eregsuser")

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
            cursor.execute(f"SET statement_timeout = '{TIMEOUT_MINUTES}min';")
            cursor.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname = 'eregs'"
            )
            cursor.execute(
                f"CREATE DATABASE {os.environ.get('DB_NAME')} WITH TEMPLATE eregs "
                f"STRATEGY FILE_COPY OWNER {db_user};"
            )
            print(f"Database {os.environ.get('DB_NAME')} has been created")
    except ProgrammingError:
        print("Database was not created, most likely because it already exists")
