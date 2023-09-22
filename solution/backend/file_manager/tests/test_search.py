import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from file_manager.models import UploadedFile


class SearchTest(TestCase):
    def check_exclusive_response(self, response, id):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.data[id]["name"])

    def login(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test_user', password='test')  # noqa: S106

    def setUp(self):
        self.login()
        self.client.force_authenticate(self.user)
        self.data = []
        with open("file_manager/tests/fixtures/sample_files.json", "r") as f:
            for i in json.load(f):
                self.data.append(i)
                UploadedFile.objects.create(**i)

    def test_no_query(self):
        response = self.client.get("/v3/file-manager/files")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data))

    def test_query_1(self):
        response = self.client.get("/v3/file-manager/files?q=test")
        self.check_exclusive_response(response, 0)

    def test_query_2(self):
        response = self.client.get("/v3/file-manager/files?q=internal+notes")
        self.check_exclusive_response(response, 1)

    def test_query_3(self):
        response = self.client.get("/v3/file-manager/files?q=policy+hello")
        self.check_exclusive_response(response, 2)

    def test_query_4(self):
        response = self.client.get("/v3/file-manager/files?q=file")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], self.data[0]["name"])
        self.assertEqual(response.data[1]["name"], self.data[2]["name"])

    def test_search_by_filename_variations(self):
        names = ["123_abc.docx", "123_abc", "123", "abc", "docx"]
        for i in names:            
            response = self.client.get(f"/v3/file-manager/files?q={i}")
            self.check_exclusive_response(response, 0)

