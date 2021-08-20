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
        print(f'loading {file}...')
        f = open(f'{content_path}/{file}')
        data = json.load(f)
        populate(data)


def populate(data):
    for category in data:
        print(f'writing {category["title"]}')
        populate_category(category)


def populate_category(category_data):
    from django.core.exceptions import ObjectDoesNotExist

    from supplementary_content.views import CategorySerializer
    from supplementary_content.models import Category

    supplementary_contents_data = category_data.pop('supplementary_content')

    try:
        category = Category.objects.get(title=category_data['title'])
    except ObjectDoesNotExist:
        category_serializer = CategorySerializer(data=category_data)
        if category_serializer.is_valid(raise_exception=True):
            category = category_serializer.save()

    update_relations(category, supplementary_contents_data)


def update_relations(category, supplementary_contents_data):
    from supplementary_content.models import SupplementaryContent, RegulationSection

    for supplementary_content_data in supplementary_contents_data:
        sections = supplementary_content_data.pop('sections')
        url = supplementary_content_data.pop('url')
        supplementary_content, _created = SupplementaryContent.objects.get_or_create(url=url, defaults={'category': category, **supplementary_content_data})

        for section in sections:
            regulation_section, _created = RegulationSection.objects.get_or_create(**section)
            regulation_section.supplementary_content.add(supplementary_content)
