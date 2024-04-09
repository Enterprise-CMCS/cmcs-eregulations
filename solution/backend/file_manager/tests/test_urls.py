import json
import unittest

from django.conf import settings  # Import the Django settings module
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from content_search.functions import index_group
from file_manager.models import Subject, UploadedFile
from resources.models import FederalRegisterDocument, SupplementalContent

c = Client()
auth_headers = {
    'Authorization': 'Api-Key MY_KEY',
}

skip_local_env = settings.CUSTOM_URL is None


# this test does not work locally. Will be addressed in EREGCSC-2304
@unittest.skipIf(skip_local_env, "Skipping this test in local environment")
class FileUploadTestCase(TestCase):
    def login(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test_user', password='test')  # noqa: S106

    def test_get_upload_link(self):
        self.login()
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('file-upload-new', kwargs={'file_name': 'test.doc'}))
        self.assertEqual(response.data['url'], 'https://s3.amazonaws.com/test_bucket')

    def test_get_upload_link_failure(self):
        self.assertRaises(Exception, self.client.post(reverse('file-upload-new', kwargs={'file_name': 'test.doc'})))

    def tearDown(self) -> None:
        self.user = None


class SubjectTest(TestCase):

    def clean_up(self):
        SupplementalContent.objects.all().delete()
        FederalRegisterDocument.objects.all().delete()
        UploadedFile.objects.all().delete()
        Subject.objects.all().delete()

    def setUp(self):
        self.clean_up()
        self.subject1 = Subject.objects.create(full_name='test')
        self.subject2 = Subject.objects.create(full_name='test2')
        with open("content_search/tests/fixtures/sample_supplemental.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                file = SupplementalContent.objects.create(**data)
                file.subjects.set([self.subject2, self.subject1])
                file.save()

        with open("content_search/tests/fixtures/sample_fr_doc.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                file = FederalRegisterDocument.objects.create(**data)
                file.subjects.set([self.subject2])
                file.save()

        with open("content_search/tests/fixtures/sample_files.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                file = UploadedFile.objects.create(**data)
                file.subjects.set([self.subject2])
                file.save()
        index_group(SupplementalContent.objects.all())
        index_group(FederalRegisterDocument.objects.all())
        index_group(UploadedFile.objects.all())

    def test_get_subject_list(self):
        response = self.client.get("/v3/file-manager/subjects")
        data = json.loads(json.dumps(response.data))
        self.assertEqual(data[0]['internal_content'], 0)
        self.assertEqual(data[0]['external_content'], 3)
        self.assertEqual(data[1]['internal_content'], 3)
        self.assertEqual(data[1]['external_content'], 6)
