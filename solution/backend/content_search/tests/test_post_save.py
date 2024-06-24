from django.test import TestCase

from content_search.models import ContentIndex
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
        pass  # TODO: implement this test once reg part post-save is hooked up
