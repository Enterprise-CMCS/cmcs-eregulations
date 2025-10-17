
from django.test import TestCase

from content_search.models import ResourceMetadata
from resources.models import (
    FederalRegisterLink,
    InternalFile,
    InternalLink,
    PublicLink,
)


class PostSaveTest(TestCase):
    def test_public_link_create(self):
        link = PublicLink.objects.create(
            document_id="test",
            url="http://www.test.com",
        )
        # Verify a ResourceMetadata object exists for the created resource
        # Will raise an exception if not
        ResourceMetadata.objects.get(resource=link)

    def test_federal_register_link_create(self):
        link = FederalRegisterLink.objects.create(
            document_id="test",
            url="http://www.test.com",
        )
        # Verify a ResourceMetadata object exists for the created resource
        # Will raise an exception if not
        ResourceMetadata.objects.get(resource=link)

    def test_internal_file_create(self):
        file = InternalFile.objects.create(
            document_id="test",
            summary="this is a test",
        )
        # Verify a ResourceMetadata object exists for the created file
        # Will raise an exception if not
        ResourceMetadata.objects.get(resource=file)

    def test_internal_link_create(self):
        link = InternalLink.objects.create(
            document_id="test",
            summary="this is a test",
        )
        # Verify a ResourceMetadata object exists for the created link
        # Will raise an exception if not
        ResourceMetadata.objects.get(resource=link)
