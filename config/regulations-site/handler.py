#!/usr/bin/env python
import os
import sys

def reg_site(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "regulations.settings.dev") 
    try:
        from django.core.management import excecute_from_command_line
    except ImportError:
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django.
            )
execute_from_command_line(['manage.py', 'runserver')
