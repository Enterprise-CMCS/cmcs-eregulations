from parsers.utils import get_ecfr_last_updated


def parser_data(request):
    last_updated = get_ecfr_last_updated()

    return {
        "parser_last_success": last_updated,
    }
