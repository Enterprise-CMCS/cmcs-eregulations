import base64
from datetime import date
from unittest.mock import patch

from django.conf import settings
from django.db import transaction
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from content_search.models import ContentIndex, IndexedRegulationText
from content_search.utils import call_text_extractor_for_reg_text
from regcore.models import Part


class RegTextIndexingTests(TestCase):
    def setUp(self):
        self.part = Part.objects.create(
            title=42,
            name=400,
            date=date(2025, 1, 1),
            document={"title": "Test Part", "children": []},
            structure={"children": []},
            depth_stack=[],
            depth=0,
        )
        self.request = RequestFactory().get("/")

    @staticmethod
    def _authenticated_client():
        credentials = base64.b64encode(
            f"{settings.HTTP_AUTH_USER}:{settings.HTTP_AUTH_PASSWORD}".encode("utf-8")
        ).decode("ascii")
        client = APIClient()
        client.defaults["HTTP_AUTHORIZATION"] = f"Basic {credentials}"
        return client

    @staticmethod
    def _metadata(part, **kwargs):
        values = {
            "part": part,
            "title": part.title,
            "date": part.date,
            "part_title": "Test Part",
            "part_number": part.name,
            "node_type": "section",
            "node_id": "1",
            "node_title": "Test section",
        }
        values.update(kwargs)
        return IndexedRegulationText.objects.create(**values)

    @override_settings(
        USE_LOCAL_TEXT_EXTRACTOR=False,
        TEXT_EXTRACTOR_ARN="arn:aws:lambda:us-east-1:123456789012:function:text-extractor",
        TEXT_EXTRACTOR_QUEUE_URL="",
    )
    @patch("content_search.utils.establish_client")
    @patch("content_search.utils._extract_via_lambda", return_value=(1, []))
    @patch("content_search.utils.index_part_node")
    def test_reg_text_extraction_dispatches_after_commit(
        self,
        mock_index_part_node,
        mock_extract,
        mock_establish_client,
    ):
        old_metadata = self._metadata(self.part)
        old_index = ContentIndex.objects.create(reg_text=old_metadata, content="old text")
        new_metadata = IndexedRegulationText(
            part=self.part,
            title=self.part.title,
            date=self.part.date,
            part_title="Test Part",
            part_number=self.part.name,
            node_type="section",
            node_id="2",
            node_title="New section",
        )
        mock_index_part_node.return_value = ([new_metadata], ["new text"])

        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            with transaction.atomic():
                queued, failures = call_text_extractor_for_reg_text(self.request, [self.part])
                self.assertEqual((queued, failures), (1, []))
                mock_extract.assert_not_called()

        old_metadata.refresh_from_db()
        self.assertIsNotNone(old_metadata.retired_at)
        self.assertFalse(ContentIndex.objects.filter(pk=old_index.pk).exists())
        self.assertEqual(len(callbacks), 1)

        callbacks[0]()

        mock_establish_client.assert_called_once_with("lambda")
        mock_extract.assert_called_once()

    @override_settings(
        USE_LOCAL_TEXT_EXTRACTOR=False,
        TEXT_EXTRACTOR_ARN="arn:aws:lambda:us-east-1:123456789012:function:text-extractor",
        TEXT_EXTRACTOR_QUEUE_URL="",
    )
    @patch("content_search.utils._extract_via_lambda", return_value=(1, []))
    @patch("content_search.utils.index_part_node")
    def test_reg_text_extraction_is_not_dispatched_after_rollback(self, mock_index_part_node, mock_extract):
        old_metadata = self._metadata(self.part)
        old_index = ContentIndex.objects.create(reg_text=old_metadata, content="old text")
        new_metadata = IndexedRegulationText(
            part=self.part,
            title=self.part.title,
            date=self.part.date,
            part_title="Test Part",
            part_number=self.part.name,
            node_type="section",
            node_id="2",
            node_title="New section",
        )
        mock_index_part_node.return_value = ([new_metadata], ["new text"])

        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            with self.assertRaises(RuntimeError):
                with transaction.atomic():
                    call_text_extractor_for_reg_text(self.request, [self.part])
                    raise RuntimeError("roll back upload")

        old_metadata.refresh_from_db()
        self.assertIsNone(old_metadata.retired_at)
        self.assertTrue(ContentIndex.objects.filter(pk=old_index.pk).exists())
        self.assertEqual(callbacks, [])
        mock_extract.assert_not_called()

    def test_retired_reg_text_callback_is_noop(self):
        metadata = self._metadata(self.part)
        metadata.retired_at = timezone.now()
        metadata.save(update_fields=["retired_at"])
        client = self._authenticated_client()

        response = client.patch(
            f"/v3/content-search/reg_text/{metadata.pk}/chunk",
            {
                "id": metadata.pk,
                "chunk_index": 0,
                "total_chunks": 1,
                "text": "stale text",
                "embedding": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(ContentIndex.objects.filter(reg_text=metadata).exists())

    def test_callback_for_metadata_from_previous_part_date_is_noop(self):
        metadata = self._metadata(self.part, date=date(2024, 1, 1))
        client = self._authenticated_client()

        response = client.patch(
            f"/v3/content-search/reg_text/{metadata.pk}/chunk",
            {
                "id": metadata.pk,
                "chunk_index": 0,
                "total_chunks": 1,
                "text": "stale text",
                "embedding": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(ContentIndex.objects.filter(reg_text=metadata).exists())
