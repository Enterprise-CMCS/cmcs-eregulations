#!/usr/bin/env python
import os


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    import django
    django.setup()

    from django.db import connection
    connection.ensure_connection()
    if not connection.is_usable():
        raise Exception("database is unreachable")
    
    from django.apps import apps
    installed_apps = []
    for app in apps.get_app_configs():
        installed_apps.append(app.label)

    from django.core.management import call_command
    for app in installed_apps:
        call_command("migrate", app)
