#!/usr/bin/env python
import os
import django
from django.db import connection


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    django.setup()

    connection.ensure_connection()
    if not connection.is_usable():
        print("database is unreachable")
    else:
        try:
            with connection.cursor() as cursor:
                db_name = os.environ.get('STAGE', '')
                query = f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}'"
                cursor.execute(query)
                cursor.execute(f"DROP DATABASE {db_name}")
                print(f"Database {db_name} has been removed")
        except Exception as e:
            print(f"An error occurred while deleting the database: {str(e)}")
