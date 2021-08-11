#!/usr/bin/env python
import os
import json


def handler(self):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    import django
    django.setup()

    content_path = '../tools/guidance_pipeline/guidance'
    content_list = os.listdir(content_path)
    for file in content_list:
        f = open(file)
        data = json.load(f)
        populate(data)


def populate(self, data):
    from supplementary_content.views import CategorySerializer
    from supplementary_content.views import SupplementaryContentSerializer
    from supplementary_content.views import RegulationSectionSerializer

    category = CategorySerializer(data=data)
    if category.is_valid():
        category.save()

    supplementary_content = SupplementaryContentSerializer(data=data['supplementary_content'])
    if supplementary_content.is_valid():
        supplementary_content.save()

    section = RegulationSectionSerializer(data=data['supplementary_content']['sections'])
    if section.is_valid():
        section.save()
