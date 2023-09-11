from .models import SiteConfiguration
import os
def site_config(request):
    config = SiteConfiguration.objects.first()
    return {
        "allow_indexing": config.allow_indexing,
    }


def eua_config(request):
    EUA_FEATUREFLAG = os.environ.get('EUA_FEATUREFLAG', 'false')

    return {
        'EUA_FEATUREFLAG': EUA_FEATUREFLAG,
    }
