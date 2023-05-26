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
                cursor.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{os.environ.get('STAGE', '')}'")
                cursor.execute(f"DROP DATABASE {os.environ.get('STAGE', '')}")
                print(f"Database {os.environ.get('STAGE', '')} has been removed")
        except Exception as e:
            print(f"An error occurred while deleting the database: {str(e)}")