from regcore.models import ECFRParserResult


def regcore_config(request):
    parserResult = list(ECFRParserResult.objects.filter(errors=0).order_by("title", "-end").distinct("title"))
    lastUpdated = sorted(parserResult, key=lambda x: x.end)[0].end if parserResult else None

    return {
        "parser_last_success": lastUpdated
    }
