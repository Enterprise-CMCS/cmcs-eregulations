from datetime import datetime, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient

from common.test_functions.common_functions import get_paginated_data
from regulations.models import SiteConfiguration
from resources.models import (
    FederalRegisterLink,
    InternalFile,
    PublicCategory,
    ResourceGroup,
    ResourcesConfiguration,
    Section,
    Subject,
)


class TestResourcesEndpoint(TestCase):
    def login(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test_user', password='test')  # noqa: S106
        self.client.force_authenticate(self.user)

    def setUp(self):
        subject = Subject.objects.create(full_name="Access to Services", short_name="Test", abbreviation="ATS")
        s1 = Section.objects.create(title=1, part=1, section_id=1)
        s2 = Section.objects.create(title=1, part=1, section_id=2)
        g1 = ResourceGroup.objects.create(id=1)
        today = datetime.today().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
        twodaysago = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')
        f1 = FederalRegisterLink.objects.create(id=1, date=today)
        f1.resource_groups.set([g1])
        f1.cfr_citations.set([s1, s2])
        f1.subjects.set([subject])
        f1.save()
        f2 = FederalRegisterLink.objects.create(id=2, date=twodaysago)
        f2.resource_groups.set([g1])
        f2.cfr_citations.set([s1, s2])
        f2.save()
        f3 = FederalRegisterLink.objects.create(id=3, date=yesterday, approved=False)
        f3.resource_groups.set([g1])
        f3.cfr_citations.set([s1, s2])
        f3.save()
        file1 = InternalFile.objects.create(id=4, date=yesterday, approved=True)
        file1.cfr_citations.set([s1, s2])
        file1.save()

    # TODO: re-implement and re-enable these tests post hybrid search switchover

    # def test_counts_logged_in(self):
    #     self.login()
    #     data = self.client.get("/v3/resources/?group_resources=false").data
    #     self.assertEqual(data["count"], 3)
    #     self.assertIn("count_url", data)
    #     data = self.client.get(data["count_url"]).data
    #     self.assertEqual(data["internal_resource_count"], 1)
    #     self.assertEqual(data["public_resource_count"], 2)

    # def test_counts_logged_out(self):
    #     data = self.client.get("/v3/resources/?group_resources=false").data
    #     self.assertEqual(data["count"], 2)
    #     self.assertIn("count_url", data)
    #     data = self.client.get(data["count_url"]).data
    #     self.assertEqual(data["internal_resource_count"], 0)
    #     self.assertEqual(data["public_resource_count"], 2)

    def test_duplicate_groups(self):
        # If groups are duplicated, then len(response.data) will be greater than 1
        # This is because all 3 created docs have the same cfr_citations
        response = self.client.get("/v3/resources/?cfr_citations=1.1.1&cfr_citations=1.1.2")
        self.assertEqual(response.status_code, 200)
        data = get_paginated_data(response)["results"]
        self.assertEqual(len(data), 1)

    def test_grouping_off(self):
        response = self.client.get("/v3/resources/?cfr_citations=1.1.1&cfr_citations=1.1.2&group_resources=false")
        self.assertEqual(response.status_code, 200)
        data = get_paginated_data(response)["results"]
        self.assertEqual(len(data), 2)

    def test_unapproved_group_members_showing(self):
        response = self.client.get("/v3/resources/?cfr_citations=1.1.1&cfr_citations=1.1.2")
        data = get_paginated_data(response)["results"]
        for i in data:
            self.assertEqual(i["approved"], True)
            for j in i["related_resources"]:
                self.assertEqual(j["approved"], True)

    def test_group_ordering_by_date(self):
        FederalRegisterLink.objects.filter(id=3).update(approved=True)
        response = self.client.get("/v3/resources/?cfr_citations=1.1.1&cfr_citations=1.1.2")
        data = get_paginated_data(response)["results"]
        self.assertEqual(data[0]["id"], 1)
        self.assertEqual(data[0]["related_resources"][0]["id"], 3)
        self.assertEqual(data[0]["related_resources"][1]["id"], 2)

    def test_unapproved_resources_showing(self):
        response = self.client.get("/v3/resources/?cfr_citations=1.1.1&cfr_citations=1.1.2&group_resources=false")
        data = get_paginated_data(response)["results"]
        for i in data:
            self.assertEqual(i["approved"], True)
            self.assertEqual(i["related_resources"], None)

    def test_subjects(self):
        response = self.client.get("/v3/resources/")
        data = get_paginated_data(response)["results"]
        self.assertIn("subjects", data[0])
        self.assertGreater(len(data[0]["subjects"]), 0)
        subject = data[0]["subjects"][0]
        self.assertEqual(subject["full_name"], "Access to Services")
        self.assertEqual(subject["short_name"], "Test")
        self.assertEqual(subject["abbreviation"], "ATS")

    def test_ensure_no_unauthorized_content(self):
        response = self.client.get("/v3/resources/")
        data = get_paginated_data(response)["results"]
        for i in data:
            self.assertNotEqual(i["type"], "internal_file")

    def test_authorized_content_viewable(self):
        self.login()
        response = self.client.get("/v3/resources/")
        data = get_paginated_data(response)["results"]
        internal_file_exists = False
        for i in data:
            if i["type"] == "internal_file":
                internal_file_exists = True
        self.assertEqual(internal_file_exists, True)


class FederalRegisterUploadIdempotencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        SiteConfiguration.get_solo()

    @patch("resources.views.resources.apps.is_installed", return_value=False)
    def test_duplicate_federal_register_upload_is_idempotent(self, mock_is_installed):
        category = PublicCategory.objects.create(name="Federal Register Links")
        config = ResourcesConfiguration.get_solo()
        config.fr_link_category = category
        config.save()
        client = APIClient()
        client.force_authenticate(User.objects.create_superuser(username="test_user", password="test"))  # noqa: S106
        payload = {
            "sections": [],
            "section_ranges": [],
            "url": "https://example.gov/document",
            "description": "A Federal Register document",
            "name": "90 FR 1",
            "docket_numbers": [],
            "document_number": "2026-12345",
            "date": "2026-01-01",
            "approved": True,
            "doc_type": "Rule",
            "raw_text_url": "https://example.gov/document.txt",
        }

        for _ in range(2):
            response = client.put("/v3/resources/public/federal_register_links", payload, format="json")
            self.assertEqual(response.status_code, 200)

        self.assertEqual(
            FederalRegisterLink.objects.filter(document_number="2026-12345").count(),
            1,
        )
        self.assertTrue(mock_is_installed.called)
