import csv

from django.contrib.admin import AdminSite
from django.test import TestCase

from resources.admin import AbstractResourceAdmin, PublicLinkAdmin
from resources.models import AbstractCategory, AbstractResource, PublicLink, Section, Subpart


class TestAdminFunctions(TestCase):
    def setUp(self):
        self.resourcesAdmin = AbstractResourceAdmin(model=AbstractResource, admin_site=AdminSite())
        self.publicLinkAdmin = PublicLinkAdmin(model=PublicLink, admin_site=AdminSite())
        Section.objects.create(title=42, part=400, section_id=200)
        Subpart.objects.create(title=42, part=433, subpart_id="A")
        AbstractCategory.objects.create(name="test")

    def test_add_resources(self):
        bulk_add, bad_locations = self.resourcesAdmin.get_bulk_locations("400.200, 5656565", "42")
        good_section = Section.objects.get(section_id=200)
        self.assertEqual(bulk_add, [good_section])
        self.assertEqual(bad_locations, [" 5656565"])

    def test_bulk_section_check(self):
        section = self.resourcesAdmin.build_location("400.200", "42")
        self.assertIsInstance(section, Section)
        section = self.resourcesAdmin.build_location("42 400.200", "")
        self.assertIsInstance(section, Section)
        section = self.resourcesAdmin.build_location("42 CFR 400.200", "")
        self.assertIsInstance(section, Section)
        section = self.resourcesAdmin.build_location("42 400 200", "")
        self.assertIsInstance(section, Section)
        section = self.resourcesAdmin.build_location("400 200", "42")
        self.assertIsInstance(section, Section)
        section = self.resourcesAdmin.build_location("42 CFR 400 200", "")
        self.assertIsInstance(section, Section)

    def test_bulk_section_check_bad(self):
        # Non existing section
        section = self.resourcesAdmin.build_location("400.500", "42")
        self.assertIsNone(None, section)
        # bad format
        section = self.resourcesAdmin.build_location("400500", "42")
        self.assertIsNone(None, section)
        # no title
        section = self.resourcesAdmin.build_location("400.500", "")
        self.assertIsNone(None, section)
        # Misspell cfr
        section = self.resourcesAdmin.build_location("42 CFdR 400 200", "")
        self.assertIsNone(None, section)
        # No section
        section = self.resourcesAdmin.build_location("42 CFR 400", "")
        self.assertIsNone(None, section)
        # No section
        section = self.resourcesAdmin.build_location("42 200", "")
        self.assertIsNone(None, section)

    def test_bulk_subpart_check(self):
        subpart = self.resourcesAdmin.build_location("42 433 Subpart A", "")
        self.assertIsInstance(subpart, Subpart)
        subpart = self.resourcesAdmin.build_location("42 CFR 433 Subpart A", "")
        self.assertIsInstance(subpart, Subpart)
        subpart = self.resourcesAdmin.build_location("42 CFR 433.A", "")
        self.assertIsInstance(subpart, Subpart)
        subpart = self.resourcesAdmin.build_location("42 433 A", "")
        self.assertIsInstance(subpart, Subpart)
        subpart = self.resourcesAdmin.build_location("433 Subpart A", "42")
        self.assertIsInstance(subpart, Subpart)
        subpart = self.resourcesAdmin.build_location("433.A", "42")
        self.assertIsInstance(subpart, Subpart)
        subpart = self.resourcesAdmin.build_location("433 A", "42")
        self.assertIsInstance(subpart, Subpart)

    def test_bulk_subpart_check_bad(self):
        # Non existing section
        subpart = self.resourcesAdmin.build_location("433.B", "42")
        self.assertIsNone(None, subpart)
        # bad format
        subpart = self.resourcesAdmin.build_location("433A", "42")
        self.assertIsNone(None, subpart)
        # no title
        subpart = self.resourcesAdmin.build_location("433.A", "")
        self.assertIsNone(None, subpart)
        # Misspell cfr
        subpart = self.resourcesAdmin.build_location("42 CFdR 433 A", "")
        self.assertIsNone(None, subpart)
        # No subpart
        subpart = self.resourcesAdmin.build_location("42 CFR 433", "")
        self.assertIsNone(None, subpart)
        # No subpart
        subpart = self.resourcesAdmin.build_location("42 433", "")
        self.assertIsNone(None, subpart)

    def test_add_public_link_content(self):
        with open("resources/tests/fixtures/test_resource.csv", newline='') as resources:
            output = csv.reader(resources, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
            results = self.publicLinkAdmin.add_content(output)
        good_section = Section.objects.get(section_id=200)
        good_category = AbstractCategory.objects.get(name="test")
        id = str(PublicLink.objects.get(name='content-1').id)
        row1 = {"name": f"<a href=/admin/resources/public/links/{id}/change/ target='blank'>content-1</a>",
                "category": good_category, "added_locations": [good_section], "failed_locations": [" 200"]}
        self.assertEqual(results[0][0], row1)
        self.assertEqual(results[1], [{'row': ['content-2'], 'line_number': 3}])
        self.assertEqual(results[0][1]["category"], "Invalid category: dkfjdlkfjd")
