from unittest.mock import patch

from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import RequestFactory, TestCase
from django.urls import reverse

from resources.admin import PublicLinkAdmin
from resources.admin.actions import mark_approved, mark_not_approved
from resources.models import PublicLink
from resources.utils import get_support_link


class AdminActionsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = PublicLinkAdmin(PublicLink, AdminSite())
        self.user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')  # noqa
        self.resource1 = PublicLink.objects.create(approved=False)
        self.resource2 = PublicLink.objects.create(approved=False)
        self.resource3 = PublicLink.objects.create(approved=False)

    def test_mark_approved(self):
        request = self.factory.post(reverse('admin:resources_publiclink_changelist'))
        request.user = self.user
        queryset = PublicLink.objects.filter(id=self.resource1.id)
        mark_approved(self.admin, request, queryset)
        resource = PublicLink.objects.get(id=self.resource1.id)
        self.assertTrue(resource.approved)

    def test_mark_not_approved(self):
        request = self.factory.post(reverse('admin:resources_publiclink_changelist'))
        request.user = self.user
        queryset = PublicLink.objects.filter(id=self.resource1.id)
        mark_not_approved(self.admin, request, queryset)
        resource = PublicLink.objects.get(id=self.resource1.id)
        self.assertFalse(resource.approved)

    @patch('resources.admin.actions.call_text_extractor')
    def test_extract_text_single_fail_single_success(self, mock_call_text_extractor):
        mock_call_text_extractor.return_value = (1, [{"id": self.resource2.id, "reason": "Invalid URL"}])

        fixtures = [self.resource1, self.resource2]

        self.client.login(username='admin', password='admin')  # noqa
        data = {"action": "extract_text", "_selected_action": [str(f.pk) for f in fixtures]}
        response = self.client.post(reverse('admin:resources_publiclink_changelist'), data)
        messages = list(get_messages(response.wsgi_request))

        # Assert the expected message is displayed to the user
        edit_url = reverse("edit", args=[self.resource2.pk])
        expected_message = (
            "Text extraction successfully started on 1 resource, but extraction failed for the following resource: "
            f"<a target=\"_blank\" href=\"{edit_url}\">{self.resource2.pk}</a>. "
            "Please be sure this item has a valid URL or attached file, then "
            f"{get_support_link('contact support')} for assistance if needed."
        )

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, expected_message)

    @patch('resources.admin.actions.call_text_extractor')
    def test_extract_text_multiple_success_single_fail(self, mock_call_text_extractor):
        mock_call_text_extractor.return_value = (2, [{"id": self.resource2.id, "reason": "Invalid URL"}])

        fixtures = [self.resource1, self.resource2, self.resource3]

        self.client.login(username='admin', password='admin')  # noqa
        data = {"action": "extract_text", "_selected_action": [str(f.pk) for f in fixtures]}
        response = self.client.post(reverse('admin:resources_publiclink_changelist'), data)
        messages = list(get_messages(response.wsgi_request))

        # Assert the expected message is displayed to the user
        edit_url = reverse("edit", args=[self.resource2.pk])
        expected_message = (
            "Text extraction successfully started on 2 resources, but extraction failed for the following resource: "
            f"<a target=\"_blank\" href=\"{edit_url}\">{self.resource2.pk}</a>. "
            "Please be sure this item has a valid URL or attached file, then "
            f"{get_support_link('contact support')} for assistance if needed."
        )

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, expected_message)

    @patch('resources.admin.actions.call_text_extractor')
    def test_extract_text_multiple_success_multiple_fail(self, mock_call_text_extractor):
        mock_call_text_extractor.return_value = (2, [
            {"id": self.resource2.id, "reason": "Invalid URL"},
            {"id": self.resource3.id, "reason": "Invalid URL"},
        ])

        fixtures = [self.resource1, self.resource2, self.resource3]

        self.client.login(username='admin', password='admin')  # noqa
        data = {"action": "extract_text", "_selected_action": [str(f.pk) for f in fixtures]}
        response = self.client.post(reverse('admin:resources_publiclink_changelist'), data)
        messages = list(get_messages(response.wsgi_request))

        # Assert the expected message is displayed to the user
        edit_url1 = reverse("edit", args=[self.resource2.pk])
        edit_url2 = reverse("edit", args=[self.resource3.pk])
        expected_message = (
            "Text extraction successfully started on 2 resources, but extraction failed for the following resources: "
            f"<a target=\"_blank\" href=\"{edit_url1}\">{self.resource2.pk}</a>, "
            f"<a target=\"_blank\" href=\"{edit_url2}\">{self.resource3.pk}</a>. "
            "Please be sure these items have valid URLs or attached files, then "
            f"{get_support_link('contact support')} for assistance if needed."
        )

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, expected_message)

    @patch('resources.admin.actions.call_text_extractor')
    def test_extract_text_multiple_failures(self, mock_call_text_extractor):
        mock_call_text_extractor.return_value = (0, [
            {"id": self.resource2.id, "reason": "Invalid URL"},
            {"id": self.resource3.id, "reason": "Invalid URL"},
        ])

        fixtures = [self.resource2, self.resource3]

        self.client.login(username='admin', password='admin')  # noqa
        data = {"action": "extract_text", "_selected_action": [str(f.pk) for f in fixtures]}
        response = self.client.post(reverse('admin:resources_publiclink_changelist'), data)
        messages = list(get_messages(response.wsgi_request))

        # Assert the expected message is displayed to the user
        edit_url1 = reverse("edit", args=[self.resource2.pk])
        edit_url2 = reverse("edit", args=[self.resource3.pk])
        expected_message = (
            "Text extraction failed for the following resources: "
            f"<a target=\"_blank\" href=\"{edit_url1}\">{self.resource2.pk}</a>, "
            f"<a target=\"_blank\" href=\"{edit_url2}\">{self.resource3.pk}</a>. "
            "Please be sure these items have valid URLs or attached files, then "
            f"{get_support_link('contact support')} for assistance if needed."
        )

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, expected_message)
