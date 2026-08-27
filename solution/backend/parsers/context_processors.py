from parsers.models import EcfrParserResult


def parser_data(request):
    try:
        last_updated = EcfrParserResult.objects.filter(success=True).order_by("-timestamp").first().timestamp
    except AttributeError:
        last_updated = None

    return {
        "parser_last_success": last_updated,
    }
