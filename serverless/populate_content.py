#!/usr/bin/env python
import os
import json


def handler(event, context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    import django
    django.setup()

    content_path = os.environ.get('SUPPLEMENTAL_CONTENT_PATH')
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
    from rest_framework import serializers
    from supplemental_content.models import Category
    from supplemental_content.views import SupplementalContentSerializer

    class CategorySerializer(serializers.ModelSerializer):
        supplemental_content = SupplementalContentSerializer(many=True, read_only=True)

        class Meta:
            model = Category
            fields = ("id", "title", "description", "supplemental_content")

    supplemental_contents_data = category_data.pop('supplemental_content')

    try:
        category = Category.objects.get(title=category_data['title'])
    except ObjectDoesNotExist:
        category_serializer = CategorySerializer(data=category_data)
        if category_serializer.is_valid(raise_exception=True):
            category = category_serializer.save()

    update_relations(category, supplemental_contents_data)


def update_relations(category, supplemental_contents_data):
    from supplemental_content.models import SupplementalContent, RegulationSection

    for supplemental_content_data in supplemental_contents_data:
        sections = supplemental_content_data.pop('sections')
        url = supplemental_content_data.pop('url')
        supplemental_content, _created = SupplementalContent.objects.get_or_create(
            url=url,
            defaults={
                'category': category,
                'approved': False,
                **supplemental_content_data
            }
        )

        for section in sections:
            regulation_section, _created = RegulationSection.objects.get_or_create(**section)
            regulation_section.supplemental_content.add(supplemental_content)
