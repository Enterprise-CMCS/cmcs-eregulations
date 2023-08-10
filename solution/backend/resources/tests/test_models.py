from django.core.exceptions import ValidationError
from django.test import TestCase

from resources.models import Section, Subpart


class TestLocationUniqueness(TestCase):
    def setUp(self):
        Section.objects.create(title=42, part=433, section_id=1)
        Subpart.objects.create(title=42, part=433, subpart_id="A")

    def test_create_dupe_section(self):
        with self.assertRaises(ValidationError):
            Section.objects.create(title=42, part=433, section_id=1)

    def test_create_dupe_subpart(self):
        with self.assertRaises(ValidationError):
            Subpart.objects.create(title=42, part=433, subpart_id="A")

    def test_overwrite(self):
        section = Section.objects.create(title=42, part=433, section_id=2)
        with self.assertRaises(ValidationError):
            section.section_id = 1
            section.save()
        subpart = Subpart.objects.create(title=42, part=433, subpart_id="B")
        with self.assertRaises(ValidationError):
            subpart.subpart_id = "A"
            subpart.save()

    def test_update_or_create(self):
        Section.objects.update_or_create(title=42, part=433, section_id=1, defaults={})
        Subpart.objects.update_or_create(title=42, part=433, subpart_id="A", defaults={})
