#!/usr/bin/env python
import os
from django.core.management import call_command


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    import django
    django.setup()

    call_command('loaddata', 'supplemental_content.category.json')
    call_command('loaddata', 'supplemental_content.subcategory.json')
    call_command('loaddata', 'supplemental_content.subpart.json')
    call_command('loaddata', 'supplemental_content.section.json')
    call_command('loaddata', 'supplemental_content.supplementalcontent.json')
