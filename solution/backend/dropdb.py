#!/usr/bin/env python

import os

import django

from django.db import connection
from django.db.utils import ProgrammingError, OperationalError

def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    django.setup()
    try:
        connection.ensure_connection()
    except OperationalError as e:
        raise Exception("Could not connect to database: {!s}".format(e))
    if not connection.is_usuable():
        raise Exception("database connection is not usable")

    try:
        with connection.cursor() as cursor:
            db_name = os.environ.get('STAGE', '')
            query = f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}'"
            cursor.execute(query)
            cursor.execute(f"DROP DATABASE {db_name}")
            print(f"Database {db_name} has been removed")
    except ProgrammingError as e:
        print(f"Database was not deleted, most likely because it does not exist: {str(e)}")
