import unittest
from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import Client
from django.urls import reverse

from content_search.models import ContentIndex
from content_search.views import EditContentView


class EditContentViewTest(unittest.TestCase):
    def setUp(self):
        # Create a user for authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()

    def test_edit_content_view_redirect(self):
        # Create a ContentIndex object for testing
        index = ContentIndex.objects.create(file=None, supplemental_content=None, fr_doc=None)

        # Set up a request
        url = reverse('edit-content', kwargs={'resource_id': index.id})
        request = HttpRequest()
        request.method = 'GET'
        request.user = self.user
        request.path_info = url

        # Mock the ContentIndex.objects.get method to return the created index
        with patch('content_search.views.ContentIndex.objects.get') as mock_get:
            mock_get.return_value = index

            # Call the get method
            response = EditContentView.as_view()(request, resource_id=index.id)

        # Assert that the response is a redirect
        self.assertEqual(response.status_code, 302)



