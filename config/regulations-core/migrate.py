#!/usr/bin/env python
import os
import sys

def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "regcore.settings.pgsql") 
    import django
    django.setup()

    from django.db import connection
    connection.ensure_connection()
    if not connection.is_usable():
        raise Exception("database is unreachable")

    from django.core.management import call_command
    call_command('migrate')
