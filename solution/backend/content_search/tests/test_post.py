import json

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from common.functions import get_tokens_for_user
from common.test_functions.common_functions import get_paginated_data
from content_search.models import ContentIndex
from resources.models import Subject, Section, PublicLink, PublicCategory, InternalCategory


class SearchTest(APITestCase):
    def check_exclusive_response(self, response, id):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_paginated_data(response)
        self.assertEqual(data['results'][0]["doc_name_string"], self.internal_docs[id]["document_name"])

    def clean_up(self):
        PublicLinks.objects.all().delete()
        PublicCategory.objects.all().delete()
        InternalCategory.objects.all().delete()
    def get_token(self):
        user = User.objects.create_superuser(username='test_user', password='test')  # noqa: S106
        return get_tokens_for_user(user)['access']

    def setUp(self):
        self.clean_up()
        self.internal_docs = []
        self.location1 = Section.objects.create(title="42", part="433", section_id="1")
        self.location2 = Section.objects.create(title="33", part="31", section_id="22")
        self.public_category = PublicCategory.objects.create(name='public test category')
        self.internal_category = InternalCategory.objects.create(name='internal test category')
        self.subject1 = Subject.objects.create()
        self.subject2 = Subject.objects.create()

        with open("content_search/tests/fixtures/sample_supplemental.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                file = PublicLinks.objects.create(**data)
                if i == 0:
                    file.locations.set([self.location2])
                    file.subjects.set([self.subject2])
                    file.category = self.public_category
                    file.save()
                elif i == 1:  # Assign internal category for another item
                    file.locations.set([self.location1])
                    file.subjects.set([self.subject1])
                    file.category = self.internal_category
                    file.save()

    def test_update_content_public_category(self):
        content = ContentIndex.objects.filter(resource__category=self.public_category).first()
        json_object = {
            'id': content.uid,
            'text': 'test public'
        }
        response = self.client.post("/v3/content-search/id/",
                                    data=json.dumps(json_object),
                                    content_type='application/json', )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post("/v3/content-search/id/",
                                    data=json.dumps(json_object),
                                    content_type='application/json', )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content.refresh_from_db()
        self.assertEqual(content.content, 'test public')

    def test_update_content_internal_category(self):
        content = ContentIndex.objects.filter(resource__category=self.internal_category).first()
        json_object = {
            'id': content.uid,
            'text': 'test internal'
        }
        response = self.client.post("/v3/content-search/id/",
                                    data=json.dumps(json_object),
                                    content_type='application/json', )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post("/v3/content-search/id/",
                                    data=json.dumps(json_object),
                                    content_type='application/json', )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content.refresh_from_db()
        self.assertEqual(content.content, 'test internal')
