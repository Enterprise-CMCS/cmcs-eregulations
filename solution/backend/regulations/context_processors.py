import os

from content_search.models import ContentSearchConfiguration

from .models import SiteConfiguration


def site_config(request):
    config = SiteConfiguration.objects.first()
    content_search_config = ContentSearchConfiguration.get_solo()
    return {
        "allow_indexing": config.allow_indexing,
        "show_flash_banner": config.show_flash_banner,
        "flash_banner_text": config.flash_banner_text,
        "default_title": config.default_title,
        "default_page_size": content_search_config.default_page_size,
    }


def eua_config(request):
    EUA_FEATUREFLAG = bool(os.getenv('EUA_FEATUREFLAG', 'False').lower() == 'true')
    return {
        'EUA_FEATUREFLAG': EUA_FEATUREFLAG,
    }
