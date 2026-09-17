from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from parsers.models import EcfrLauncherResult, EcfrParserResult


class ParsersApiTestCase(APITestCase):
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
