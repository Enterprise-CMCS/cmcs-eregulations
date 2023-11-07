import json

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from common.functions import get_tokens_for_user
from common.test_functions.common_functions import get_paginated_data
from content_search.functions import index_group
from content_search.models import ContentIndex
from file_manager.models import Subject
from resources.models import Category, Section, SupplementalContent


class SearchTest(APITestCase):
    def check_exclusive_response(self, response, id):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_paginated_data(response)
        self.assertEqual(data['results'][0]["doc_name_string"], self.internal_docs[id]["document_name"])

    def clean_up(self):
        SupplementalContent.objects.all().delete()

    def get_token(self):
        user = User.objects.create_superuser(username='test_user', password='test')  # noqa: S106
        return get_tokens_for_user(user)['access']

    def setUp(self):
        self.clean_up()
        self.internal_docs = []
        self.location1 = Section.objects.create(title="42", part="433", section_id="1")
        self.location2 = Section.objects.create(title="33", part="31", section_id="22")
        category = Category.objects.create(name='test category')
        self.subject1 = Subject.objects.create()
        self.subject2 = Subject.objects.create()

        with open("content_search/tests/fixtures/sample_supplemental.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                file = SupplementalContent.objects.create(**data)
                if i == 0:  # only assign location and subject on item 0
                    file.locations.set([self.location2])
                    file.subjects.set([self.subject2])
                    file.category = category
                    file.save()

        index_group(SupplementalContent.objects.all())

    def test_update_content(self):
        content = ContentIndex.objects.first()
        json_object = {
            'id': content.uid,
            'text': 'test'
        }
        response = self.client.post("/v3/content-search/id/",
                                    data=json.dumps(json_object),
                                    content_type='application/json',)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post("/v3/content-search/id/",
                                    data=json.dumps(json_object),
                                    content_type='application/json',)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = ContentIndex.objects.first()
        self.assertEqual(content.content, 'test')
