from django.http.response import HttpResponse

from regulations.models import SiteConfiguration


class NoIndex:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config = SiteConfiguration.objects.first()
        response = self.get_response(request)
        if not config.allow_indexing:
            response["X-Robots-Tag"] = "noindex"
        return response
