from parsers.models import EcfrParserResult


def regcore_config(request):
    parserResult = list(EcfrParserResult.objects.filter(success=True).order_by("title", "-timestamp").distinct("title"))
    lastUpdated = sorted(parserResult, key=lambda x: x.timestamp)[0].timestamp if parserResult else None

    return {
        "parser_last_success": lastUpdated
    }
