#!/usr/bin/env python

import os

import django
from django.db import connections
from django.db.utils import ProgrammingError


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

    db_name = os.environ.get('DB_NAME', '')  # Should not fail
    if db_name.lower() in ["dev", "val", "prod", "eregs"]:
        print("This is not an ephemeral database, skipping deletion.")
        return

    try:
        with connection.cursor() as cursor:
            query = f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() "\
                    f"AND datname = '{db_name}'"  # noqa: S608
            cursor.execute(query)
            cursor.execute(f"DROP DATABASE {db_name} WITH ( FORCE )")
            print(f"Database {db_name} has been removed")
    except ProgrammingError as e:
        print(f"Database was not deleted, most likely because it does not exist: {str(e)}")
