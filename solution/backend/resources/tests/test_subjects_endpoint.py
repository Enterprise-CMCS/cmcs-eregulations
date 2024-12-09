
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from resources.models import (
    FederalRegisterLink,
    InternalFile,
    Subject,
)


class TestResourcesEndpoint(TestCase):
    def login(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test_user', password='test')  # noqa: S106
        self.client.force_authenticate(self.user)

    def setUp(self):
        subject1 = Subject.objects.create(full_name="Access to Services", short_name="Subj1", abbreviation="ATS")
        subject2 = Subject.objects.create(full_name="Subject 2", short_name="Subj2", abbreviation="S2")

        f1 = FederalRegisterLink.objects.create(approved=True)
        f1.subjects.set([subject1])
        f1.save()

        f2 = FederalRegisterLink.objects.create(approved=True)
        f2.subjects.set([subject1])
        f2.save()

        f3 = FederalRegisterLink.objects.create(approved=False)
        f3.subjects.set([subject1, subject2])
        f3.save()

        file1 = InternalFile.objects.create(approved=True)
        file1.subjects.set([subject1])
        file1.save()

        file2 = InternalFile.objects.create(approved=False)
        file2.subjects.set([subject1, subject2])
        file2.save()

    def test_subjects_endpoint_logged_in(self):
        self.login()
        data = self.client.get("/v3/resources/subjects").data
        self.assertEqual(data["count"], 2)

        self.assertEqual(data["results"][0]["public_resources"], 2)
        self.assertEqual(data["results"][0]["internal_resources"], 1)
        self.assertEqual(data["results"][0]["full_name"], "Access to Services")
        self.assertEqual(data["results"][0]["short_name"], "Subj1")
        self.assertEqual(data["results"][0]["abbreviation"], "ATS")

        self.assertEqual(data["results"][1]["public_resources"], 0)
        self.assertEqual(data["results"][1]["internal_resources"], 0)
        self.assertEqual(data["results"][1]["full_name"], "Subject 2")
        self.assertEqual(data["results"][1]["short_name"], "Subj2")
        self.assertEqual(data["results"][1]["abbreviation"], "S2")

    def test_subjects_endpoint_logged_out(self):
        data = self.client.get("/v3/resources/subjects").data
        self.assertEqual(data["count"], 2)

        self.assertEqual(data["results"][0]["public_resources"], 2)
        self.assertEqual(data["results"][0]["internal_resources"], 0)
        self.assertEqual(data["results"][0]["full_name"], "Access to Services")
        self.assertEqual(data["results"][0]["short_name"], "Subj1")
        self.assertEqual(data["results"][0]["abbreviation"], "ATS")

        self.assertEqual(data["results"][1]["public_resources"], 0)
        self.assertEqual(data["results"][1]["internal_resources"], 0)
        self.assertEqual(data["results"][1]["full_name"], "Subject 2")
        self.assertEqual(data["results"][1]["short_name"], "Subj2")
        self.assertEqual(data["results"][1]["abbreviation"], "S2")
