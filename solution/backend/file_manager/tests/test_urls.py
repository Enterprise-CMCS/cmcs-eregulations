import unittest

from django.conf import settings  # Import the Django settings module
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

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
