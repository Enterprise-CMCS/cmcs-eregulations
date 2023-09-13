
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

c = Client()
auth_headers = {
    'Authorization': 'Api-Key MY_KEY',
}


class FileUploadTestCase(TestCase):
    def test_get_upload_link(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test_user', password='test')  # noqa: S106

        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('file-upload-new', kwargs={'file_name': 'test.doc'}))
        self.assertEqual(response.data['url'], 'https://s3.amazonaws.com/test_bucket')
