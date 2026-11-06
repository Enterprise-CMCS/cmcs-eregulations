#!/usr/bin/env python

import os
import re

import django
from django.db import connections
from django.db.utils import ProgrammingError

PERMANENT_DATABASE_NAMES = frozenset({"dev", "val", "prod", "eregs"})
EPHEMERAL_DATABASE_PATTERN = re.compile(r"^eph_[a-z0-9_]+$")
DATABASE_NOT_FOUND_CODE = "3D000"


def _validate_database_name(database_name):
    if database_name.lower() in PERMANENT_DATABASE_NAMES:
        return False

    if not EPHEMERAL_DATABASE_PATTERN.fullmatch(database_name):
        raise ValueError(
            "DB_NAME must be a generated ephemeral database name starting with 'eph_'"
        )

    return True


def _database_exists(cursor, database_name):
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (database_name,),
    )
    return cursor.fetchone() is not None


def _delete_database(connection, database_name):
    with connection.cursor() as cursor:
        if not _database_exists(cursor, database_name):
            print(f"Database {database_name} was already absent")
            return "already_absent"

        cursor.execute(
            "SELECT pg_terminate_backend(pid) "
            "FROM pg_stat_activity "
            "WHERE pid <> pg_backend_pid() AND datname = %s",
            (database_name,),
        )

        try:
            cursor.execute(
                f"DROP DATABASE {connection.ops.quote_name(database_name)} WITH ( FORCE )"
            )
        except ProgrammingError as error:
            if getattr(error, "pgcode", None) == DATABASE_NOT_FOUND_CODE:
                print(f"Database {database_name} was already absent")
                return "already_absent"
            raise

        if _database_exists(cursor, database_name):
            raise RuntimeError(f"Database {database_name} still exists after deletion")

    print(f"Database {database_name} has been removed")
    return "deleted"


def handler(event, context):
    db_name = os.environ.get("DB_NAME", "")
    if not _validate_database_name(db_name):
        print("This is not an ephemeral database, skipping deletion.")
        return {"database": db_name, "status": "skipped"}

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    django.setup()

    try:
        connection = connections["postgres"]
        connection.connect()
        connection.ensure_connection()
        if not connection.is_usable():
            raise Exception("database connection is not usable")
    except Exception as error:
        raise RuntimeError(f"Failed to connect to the database: {error}") from error

    status = _delete_database(connection, db_name)
    return {"database": db_name, "status": status}
