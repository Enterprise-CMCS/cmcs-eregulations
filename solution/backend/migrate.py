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

    from django.core.management import CommandError, call_command
    try:
        call_command("migrate")
    except CommandError:
        pass
