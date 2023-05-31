#!/usr/bin/env python

import os

import django
from django.db import connections
from django.db.utils import ProgrammingError


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
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
            db_name = os.environ.get('STAGE', '')
            query = f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}'"
            cursor.execute(query)
            cursor.execute(f"DROP DATABASE {db_name}")
            print(f"Database {db_name} has been removed")
    except ProgrammingError as e:
        print(f"Database was not deleted, most likely because it does not exist: {str(e)}")
