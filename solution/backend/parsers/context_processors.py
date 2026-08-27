from parsers.models import EcfrLauncherResult, EcfrParserResult


def parser_data(request):
    launcher_results = list(EcfrLauncherResult.objects.order_by("-timestamp"))
    last_updated = None

    for index, launcher_result in enumerate(launcher_results):
        upper_bound = launcher_results[index - 1].timestamp if index > 0 else None

        worker_results = EcfrParserResult.objects.filter(timestamp__gte=launcher_result.timestamp)
        if upper_bound is not None:
            worker_results = worker_results.filter(timestamp__lt=upper_bound)

        if not worker_results.exists():
            last_updated = launcher_result.timestamp
            break

        latest_success = worker_results.filter(success=True).order_by("-timestamp").first()
        if latest_success is not None:
            last_updated = latest_success.timestamp
            break

    if last_updated is None:
        latest_success = EcfrParserResult.objects.filter(success=True).order_by("-timestamp").first()
        if latest_success is not None:
            last_updated = latest_success.timestamp

    return {
        "parser_last_success": last_updated,
    }
