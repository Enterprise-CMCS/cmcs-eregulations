from .models import SiteConfiguration


def site_config(request):
    config = SiteConfiguration.objects.first()
    return {
        "allow_indexing": config.allow_indexing,
    }
