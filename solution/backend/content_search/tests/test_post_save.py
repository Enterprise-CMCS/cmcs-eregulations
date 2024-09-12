import json

from django.test import TestCase

from content_search.models import ContentIndex
from regcore.models import Part
from resources.models import (
    InternalFile,
    PublicLink,
)


class PostSaveTest(TestCase):
    def test_public_link_create(self):
        link = PublicLink.objects.create(
            document_id="test",
            url="http://www.test.com",
        )
        # Verify a ContentIndex object exists for the created resource
        # Will raise an exception if not
        ContentIndex.objects.get(resource=link)

    def test_internal_file_create(self):
        file = InternalFile.objects.create(
            document_id="test",
            summary="this is a test",
        )
        # Verify a ContentIndex object exists for the created file
        # Will raise an exception if not
        ContentIndex.objects.get(resource=file)

    def test_reg_part_create(self):
        with open("content_search/tests/fixtures/part.json", "r") as f:
            part = Part.objects.create(**json.load(f))

        # Verify a ContentIndex object and an IndexedRegulationText object exists for the created part
        # Will raise an exception if not
        self.assertTrue(ContentIndex.objects.filter(reg_text__part=part).count() > 0)
