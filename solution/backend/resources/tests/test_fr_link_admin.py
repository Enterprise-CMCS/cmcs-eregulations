import json
from unittest.mock import patch

from django.contrib import messages
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from resources.admin import FederalRegisterLinkAdmin
from resources.models import FederalRegisterLink


class FederalRegisterLinkExtractUrlTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = FederalRegisterLinkAdmin(FederalRegisterLink, AdminSite())
        self.user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')  # noqa
        self.link = FederalRegisterLink.objects.create(title='Test Link')

    @patch('resources.admin.requests.get')
    @patch('resources.admin.resources.call_text_extractor')
    def test_save_model_new_link(self, mock_call_text_extractor, mock_get):
        mock_get.return_value = MockResponse(
            content=json.dumps({"raw_text_url": "https://example.com/raw_text"}),
            status_code=200
        )
        mock_call_text_extractor.return_value = (1, [])

        request = self.factory.post(reverse('admin:resources_federalregisterlink_add'))
        session_middleware = SessionMiddleware(request)
        session_middleware.process_request(request)
        message_middleware = MessageMiddleware(request)
        message_middleware.process_request(request)
        request.user = self.user

        form_data = {
            "url": "https://example.com",
            "title": "Test Link 2",
            "document_number": "12345",
            "action_type": "Action",
            "approved": True,
        }

        form = self.admin.get_form(request)(data=form_data)
        form.is_valid()

        self.admin.save_model(request, form.instance, form, True)

        link = FederalRegisterLink.objects.get(title='Test Link 2')
        self.assertEqual(link.extract_url, "https://example.com/raw_text")

        response_messages = list(get_messages(request))
        self.assertEqual(len(response_messages), 0)

    @patch('resources.admin.requests.get')
    @patch('resources.admin.resources.call_text_extractor')
    def test_save_model_existing_link(self, mock_call_text_extractor, mock_get):
        mock_get.return_value = MockResponse(
            content=json.dumps({"raw_text_url": "https://example.com/raw_text"}),
            status_code=200
        )
        mock_call_text_extractor.return_value = (1, [])

        request = self.factory.post(reverse('admin:resources_federalregisterlink_change', args=[self.link.id]))
        session_middleware = SessionMiddleware(request)
        session_middleware.process_request(request)
        message_middleware = MessageMiddleware(request)
        message_middleware.process_request(request)
        request.user = self.user

        form_data = {
            "url": "https://example.com",
            "title": "Test Link",
            "document_number": "12345",
            "action_type": "Action",
            "approved": True,
        }

        form = self.admin.get_form(request)(data=form_data, instance=self.link)
        form.is_valid()

        self.admin.save_model(request, form.instance, form, False)

        link = FederalRegisterLink.objects.get(title='Test Link')
        self.assertEqual(link.extract_url, "https://example.com/raw_text")

        response_messages = list(get_messages(request))
        self.assertEqual(len(response_messages), 0)

    @patch('resources.admin.requests.get')
    @patch('resources.admin.resources.call_text_extractor')
    def test_save_model_failed_request(self, mock_call_text_extractor, mock_get):
        mock_get.return_value = MockResponse(status_code=500)
        mock_call_text_extractor.return_value = (1, [])

        request = self.factory.post(reverse('admin:resources_federalregisterlink_add'))
        session_middleware = SessionMiddleware(request)
        session_middleware.process_request(request)
        message_middleware = MessageMiddleware(request)
        message_middleware.process_request(request)
        request.user = self.user

        form_data = {
            "url": "https://example.com",
            "title": "Test Link 2",
            "document_number": "12345",
            "action_type": "Action",
            "approved": True,
        }

        form = self.admin.get_form(request)(data=form_data)
        form.is_valid()

        self.admin.save_model(request, form.instance, form, True)

        link = FederalRegisterLink.objects.get(title='Test Link 2')
        self.assertEqual(link.extract_url, "")

        response_messages = list(get_messages(request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.WARNING)
        self.assertIn("Failed to retrieve the URL used for extracting raw text", response_messages[0].message)


class MockResponse:
    def __init__(self, content=None, status_code=200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("Error")
