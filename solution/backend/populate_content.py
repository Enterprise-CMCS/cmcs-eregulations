#!/usr/bin/env python
import os
from django.core.management import call_command


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    import django
    django.setup()

    call_command('loaddata', 'resources.category.json')
    call_command('loaddata', 'resources.subcategory.json')
    call_command('loaddata', 'resources.subpart.json')
    call_command('loaddata', 'resources.section.json')
    call_command('loaddata', 'resources.supplementalcontent.json')
    call_command('loaddata', 'resources.federalregisterdocumentgroup.json')
    call_command('loaddata', 'resources.federalregisterdocument.json')
    call_command('loaddata', 'resources.resourcesconfiguration.json')
    call_command('loaddata', 'search.synonym.json')
