from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from parsers.models import EcfrLauncherResult, EcfrParserResult
from parsers.utils import get_ecfr_last_updated
from regcore.models import Part


class ParsersApiTestCase(APITestCase):
    def _authenticate_parser(self):
        self.client.force_authenticate(user=User.objects.create_user(username="parser"))

    def test_processed_dates_by_title_returns_latest_terminal_date_per_part(self):
        launcher = EcfrLauncherResult.objects.create(success=True, log="")
        now = timezone.now()

        EcfrParserResult.objects.create(
            launcher_result=launcher,
            title=42,
            part=400,
            date="2024-12-01",
            status=EcfrParserResult.STATUS_SUCCEEDED,
            status_updated_at=now - timedelta(days=2),
            success=True,
            log="",
        )
        EcfrParserResult.objects.create(
            launcher_result=launcher,
            title=42,
            part=400,
            date="2025-01-01",
            status=EcfrParserResult.STATUS_SUCCEEDED,
            status_updated_at=now,
            invalidated_at=now + timedelta(minutes=2),
            success=True,
            log="",
        )
        EcfrParserResult.objects.create(
            launcher_result=launcher,
            title=42,
            part=401,
            date="2025-01-03",
            status=EcfrParserResult.STATUS_FAILED,
            status_updated_at=now + timedelta(minutes=1),
            success=False,
            log="boom",
        )
        EcfrParserResult.objects.create(
            launcher_result=launcher,
            title=42,
            part=401,
            date="2025-01-02",
            status=EcfrParserResult.STATUS_SKIPPED,
            status_updated_at=now - timedelta(minutes=1),
            success=True,
            log="",
        )
        EcfrParserResult.objects.create(
            launcher_result=launcher,
            title=43,
            part=500,
            date="2025-01-04",
            status=EcfrParserResult.STATUS_SUCCEEDED,
            status_updated_at=now,
            success=True,
            log="",
        )

        response = self.client.get("/v3/parsers/ecfr/results/title/42/processed-dates")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            response.data,
            [
                {"part": 400, "date": "2024-12-01"},
                {"part": 401, "date": "2025-01-02"},
            ],
        )

    def test_latest_ecfr_result_ignores_invalidated_rows(self):
        launcher = EcfrLauncherResult.objects.create(success=True, log="")
        now = timezone.now()

        EcfrParserResult.objects.create(
            launcher_result=launcher,
            title=42,
            part=400,
            date="2025-01-01",
            status=EcfrParserResult.STATUS_SUCCEEDED,
            status_updated_at=now,
            invalidated_at=now + timedelta(minutes=1),
            success=True,
            log="stale",
        )
        EcfrParserResult.objects.create(
            launcher_result=launcher,
            title=42,
            part=400,
            date="2024-12-01",
            status=EcfrParserResult.STATUS_SUCCEEDED,
            status_updated_at=now - timedelta(days=1),
            success=True,
            log="active",
        )

        response = self.client.get("/v3/parsers/ecfr/results/title/42/part/400")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data["date"], "2024-12-01")

    def test_last_updated_scoped_ignores_invalidated_rows(self):
        launcher = EcfrLauncherResult.objects.create(success=True, log="")
        now = timezone.now()
        EcfrParserResult.objects.create(
            launcher_result=launcher,
            title=42,
            part=400,
            date="2025-01-01",
            status=EcfrParserResult.STATUS_SUCCEEDED,
            status_updated_at=now,
            invalidated_at=now + timedelta(minutes=1),
            success=True,
            log="stale",
        )

        self.assertIsNone(get_ecfr_last_updated(title=42, part=400))

    def test_last_updated_global_ignores_invalidated_launcher_results(self):
        active_launcher = EcfrLauncherResult.objects.create(success=True, log="")
        invalidated_launcher = EcfrLauncherResult.objects.create(success=True, log="")
        now = timezone.now()

        EcfrParserResult.objects.create(
            launcher_result=active_launcher,
            title=42,
            part=400,
            date="2025-01-01",
            status=EcfrParserResult.STATUS_SUCCEEDED,
            status_updated_at=now - timedelta(days=1),
            success=True,
            log="active",
        )
        EcfrParserResult.objects.create(
            launcher_result=invalidated_launcher,
            title=42,
            part=401,
            date="2025-01-02",
            status=EcfrParserResult.STATUS_SUCCEEDED,
            status_updated_at=now,
            invalidated_at=now + timedelta(minutes=1),
            success=True,
            log="stale",
        )

        self.assertEqual(get_ecfr_last_updated(), now - timedelta(days=1))

    def test_duplicate_ecfr_result_completion_is_idempotent(self):
        self._authenticate_parser()
        result = EcfrParserResult.objects.create(
            title=42,
            part=400,
            date="2025-01-01",
            status=EcfrParserResult.STATUS_QUEUED,
            status_updated_at=timezone.now(),
            success=False,
            log="",
        )

        for _ in range(2):
            response = self.client.patch(
                f"/v3/parsers/ecfr/results/{result.pk}",
                {"status": EcfrParserResult.STATUS_SUCCEEDED},
                format="json",
            )
            self.assertEqual(status.HTTP_200_OK, response.status_code)

        result.refresh_from_db()
        self.assertEqual(result.status, EcfrParserResult.STATUS_SUCCEEDED)
        self.assertTrue(result.success)
        self.assertEqual(EcfrParserResult.objects.filter(pk=result.pk).count(), 1)

    def test_ecfr_launcher_result_update_targets_requested_id(self):
        self._authenticate_parser()
        older = EcfrLauncherResult.objects.create(success=True, log="older")
        newer = EcfrLauncherResult.objects.create(success=True, log="newer")

        response = self.client.patch(
            f"/v3/parsers/ecfr/launcher-results/{older.pk}",
            {"success": False, "log": "older failed"},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        older.refresh_from_db()
        newer.refresh_from_db()
        self.assertFalse(older.success)
        self.assertEqual(older.log, "older failed")
        self.assertTrue(newer.success)
        self.assertEqual(newer.log, "newer")

    @patch("content_search.utils.call_text_extractor_for_reg_text", return_value=(1, []))
    def test_duplicate_ecfr_part_upload_is_idempotent(self, mock_extract):
        self._authenticate_parser()
        payload = {
            "name": "400",
            "title": "42",
            "date": "2025-01-01",
            "document": {"label": "first"},
            "structure": {"type": "PART", "children": [{"type": "SUBPART", "children": []}]},
            "depth": 0,
            "sections": [],
            "subparts": [],
            "upload_reg_text": True,
            "upload_locations": True,
        }

        for document_label in ("first", "second"):
            payload["document"]["label"] = document_label
            response = self.client.put("/v3/parsers/ecfr/parts", payload, format="json")
            self.assertEqual(status.HTTP_200_OK, response.status_code)

        part = Part.objects.get(title=42, name=400)
        self.assertEqual(Part.objects.filter(title=42, name=400).count(), 1)
        self.assertEqual(part.document["label"], "second")
        self.assertEqual(mock_extract.call_count, 2)
