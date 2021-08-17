#!/usr/bin/env python
import os
import json


def handler(self):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    import django
    django.setup()

    content_path = os.environ.get('SUPPLEMENTARY_CONTENT_PATH')
    content_list = os.listdir(content_path)
    for file in content_list:
        f = open(file)
        data = json.load(f)
        populate(data)


def populate(self, data):
    for category in data:
        populate_category(category)


def populate_category(category_data):
    from supplementary_content.views import CategorySerializer

    category = CategorySerializer(data=category_data)
    if category.is_valid():
        category.save()
