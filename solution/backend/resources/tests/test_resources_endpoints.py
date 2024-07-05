from datetime import datetime, timedelta

from django.test import TestCase

from resources.models import (
    FederalRegisterLink,
    PublicLink,
    ResourceGroup,
    Section,
    Subject,
)


class TestResourcesEndpoint(TestCase):
    def setUp(self):
        subject = Subject.objects.create(full_name="Access to Services", short_name="Test", abbreviation="ATS")
        s1 = Section.objects.create(title=1, part=1, section_id=1)
        s2 = Section.objects.create(title=1, part=1, section_id=2)
        g1 = ResourceGroup.objects.create(id=1)
        today = datetime.today().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
        twodaysago = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')
        f1 = FederalRegisterLink.objects.create(id=1, group=g1, date=today)
        f1.cfr_citations.set([s1, s2])
        f1.subjects.set([subject])
        f1.save()
        f2 = FederalRegisterLink.objects.create(id=2, group=g1, date=twodaysago)
        f2.cfr_citations.set([s1, s2])
        f2.save()
        f3 = FederalRegisterLink.objects.create(id=3, group=g1, date=yesterday, approved=False)
        f3.cfr_citations.set([s1, s2])
        f3.save()

    def test_duplicate_groups(self):
        # If groups are duplicated, then len(response.data) will be greater than 1
        # This is because all 3 created docs have the same cfr_citations
        response = self.client.get("/v3/resources/?cfr_citations=1.1.1&cfr_citations=1.1.2&paginate=false")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_unapproved_showing(self):
        response = self.client.get("/v3/resources/?cfr_citations=1.1.1&cfr_citations=1.1.2&paginate=false")
        for i in response.data:
            self.assertEqual(i["approved"], True)
            if "related_docs" in i:
                for j in i["related_docs"]:
                    self.assertEqual(j["approved"], True)

    def test_subjects(self):
        response = self.client.get("/v3/resources/?paginate=false")
        self.assertIn("subjects", response.data[0])
        self.assertGreater(len(response.data[0]["subjects"]), 0)
        subject = response.data[0]["subjects"][0]
        self.assertEqual(subject["full_name"], "Access to Services")
        self.assertEqual(subject["short_name"], "Test")
        self.assertEqual(subject["abbreviation"], "ATS")


class TestPublicLinkEndpoint(TestCase):
    def setUp(self):
        subject = Subject.objects.create(full_name="Access to Services", short_name="Test", abbreviation="ATS")
        section = Section.objects.create(title=1, part=1, section_id=1)
        resource = PublicLink.objects.create(id=1)
        resource.cfr_citations.set([section])
        resource.subjects.set([subject])
        resource.save()

    def test_subjects(self):
        response = self.client.get("/v3/resources/public/links?paginate=false")
        subject_data = response.data['results'][0]
        self.assertIn("subjects", subject_data)
        self.assertGreater(len(subject_data["subjects"]), 0)
        subject = subject_data["subjects"][0]
        self.assertEqual(subject["full_name"], "Access to Services")
        self.assertEqual(subject["short_name"], "Test")
        self.assertEqual(subject["abbreviation"], "ATS")


class TestFRDocEndpoint(TestCase):
    def setUp(self):
        subject = Subject.objects.create(full_name="Access to Services", short_name="Test", abbreviation="ATS")
        section = Section.objects.create(title=1, part=1, section_id=1)
        resource = FederalRegisterLink.objects.create(id=1)
        resource.cfr_citations.set([section])
        resource.subjects.set([subject])
        resource.save()

    def test_subjects(self):
        response = self.client.get("/v3/resources/public/federal_register_links?paginate=false")
        print(response.status_code)
        print(response.data)  # Debugging statement
        subject_data = response.data['results'][0]
        self.assertIn("subjects", subject_data)
        self.assertGreater(len(subject_data["subjects"]), 0)
        subject = subject_data["subjects"][0]
        self.assertEqual(subject["full_name"], "Access to Services")
        self.assertEqual(subject["short_name"], "Test")
        self.assertEqual(subject["abbreviation"], "ATS")
