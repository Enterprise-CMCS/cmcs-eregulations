from datetime import datetime

from django.db.models import Max

from parsers.models import EcfrLauncherResult, EcfrParserResult


def get_ecfr_last_updated(title: int | None = None, part: int | None = None) -> datetime | None:
    """Return the last-updated timestamp for eCFR parser activity.

    Scope:
    - no args: global
    - title only: title scope
    - title + part: title/part scope
    """

    if part is not None and title is None:
        raise ValueError("part requires title")

    if title is not None and part is not None:
        latest = (
            EcfrParserResult.objects.filter(
                title=title,
                part=part,
                status__in=[EcfrParserResult.STATUS_SKIPPED, EcfrParserResult.STATUS_SUCCEEDED],
            )
            .order_by("-status_updated_at")
            .first()
        )
        return latest.status_updated_at if latest is not None else None

    if title is not None:
        latest = (
            EcfrParserResult.objects.filter(
                title=title,
                status__in=[EcfrParserResult.STATUS_SKIPPED, EcfrParserResult.STATUS_SUCCEEDED],
            )
            .order_by("-status_updated_at")
            .first()
        )
        return latest.status_updated_at if latest is not None else None

    for launcher_result in EcfrLauncherResult.objects.order_by("-timestamp"):
        results = EcfrParserResult.objects.filter(launcher_result=launcher_result)
        if not results.exists():
            continue

        if results.filter(status=EcfrParserResult.STATUS_QUEUED).exists():
            continue

        if results.filter(status=EcfrParserResult.STATUS_FAILED).exists():
            continue

        aggregate = results.aggregate(latest=Max("status_updated_at"))
        if aggregate["latest"] is not None:
            return aggregate["latest"]

    return None
