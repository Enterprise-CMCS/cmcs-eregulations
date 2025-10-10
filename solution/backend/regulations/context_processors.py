import os

from .models import SiteConfiguration


def site_config(request):
    config = SiteConfiguration.objects.first()
    return {
        "allow_indexing": config.allow_indexing,
        "show_flash_banner": config.show_flash_banner,
        "flash_banner_text": config.flash_banner_text,
        "default_title": config.default_title,
    }


def eua_config(request):
    EUA_FEATUREFLAG = bool(os.getenv('EUA_FEATUREFLAG', 'False').lower() == 'true')
    return {
        'EUA_FEATUREFLAG': EUA_FEATUREFLAG,
    }
