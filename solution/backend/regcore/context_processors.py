from regcore.models import ECFRParserResult


def regcore_config(request):
    parserResult = ECFRParserResult.objects.filter(errors=0).order_by("-end").first()

    return {
        "parser_last_success": parserResult.end if parserResult else None,
    }
