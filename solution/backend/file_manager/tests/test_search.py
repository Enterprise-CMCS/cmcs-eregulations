import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from common.test_functions.common_functions import get_paginated_data
from file_manager.models import Subject, UploadedFile
from resources.models import Section


# This test is separate from the SearchTest class because all tests are authenticated within that class
class SearchTestNotLoggedIn(TestCase):
    def test_not_logged_in(self):
        response = self.client.get("/v3/file-manager/files?q=test+search")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SearchTest(TestCase):
    def check_exclusive_response(self, response, id):
        data = get_paginated_data(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]["document_name"], self.data[id]["document_name"])

    def login(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test_user', password='test')  # noqa: S106

    def setUp(self):
        self.login()
        self.client.force_authenticate(self.user)
        self.data = []

        self.location1 = Section.objects.create(title="42", part="433", section_id="1")
        self.location2 = Section.objects.create(title="33", part="31", section_id="22")

        self.subject1 = Subject.objects.create()
        self.subject2 = Subject.objects.create()

        with open("file_manager/tests/fixtures/sample_files.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                self.data.append(data)
                file = UploadedFile.objects.create(**data)
                if i == 0:  # only assign location and subject on item 0
                    file.locations.set([self.location2])
                    file.subjects.set([self.subject2])
                    file.save()

    def test_no_query(self):
        response = self.client.get("/v3/file-manager/files")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_paginated_data(response)
        self.assertEqual(data['count'], len(self.data))

    def test_single_response_queries(self):
        # This tests to ensure files are correctly *excluded* based on search terms
        tests = [("test", 0), ("internal+notes", 1), ("policy+hello", 2)]
        for i in tests:
            response = self.client.get(f"/v3/file-manager/files?q={i[0]}")
            self.check_exclusive_response(response, i[1])

    def test_multi_response_query(self):
        # This tests to ensure files are correctly *included* based on search terms
        response = self.client.get("/v3/file-manager/files?q=file")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_paginated_data(response)
        self.assertEqual(data['count'], 2)
        self.assertEqual(data['results'][0]["document_name"], self.data[0]["document_name"])
        self.assertEqual(data['results'][1]["document_name"], self.data[2]["document_name"])

    def test_search_by_filename_variations(self):
        names = ["123_abc.docx", "123_abc", "123", "abc", "docx"]
        for i in names:
            response = self.client.get(f"/v3/file-manager/files?q={i}")
            self.check_exclusive_response(response, 0)

    def test_inclusive_location_filter(self):
        response = self.client.get("/v3/file-manager/files?q=test&locations=42.433")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_paginated_data(response)
        self.assertEqual(data['count'], 0)

        response = self.client.get("/v3/file-manager/files?q=test&locations=42.433&locations=33.31")
        self.check_exclusive_response(response, 0)

    def test_inclusive_subject_filter(self):
        response = self.client.get(f"/v3/file-manager/files?q=test&subjects={self.subject1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_paginated_data(response)
        self.assertEqual(data['count'], 0)

        response = self.client.get(f"/v3/file-manager/files?q=test&subjects={self.subject1.id}&subjects={self.subject2.id}")
        self.check_exclusive_response(response, 0)
