#!/usr/bin/env python
import os


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    import django
    django.setup()
    from common.functions import loadSeedData
    loadSeedData()
