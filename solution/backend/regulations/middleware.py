import json
import traceback

from django.http.response import HttpResponse

from regulations.models import SiteConfiguration


class ProcessResponse:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config = SiteConfiguration.objects.first()
        response = self.get_response(request)

        # Add Strict-Transport-Security header if HTTPS
        if request.is_secure() and not response.get("Strict-Transport-Security"):
            response["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

        # Add X-Robots-Tag header based on configuration
        if not config.allow_indexing:
            response["X-Robots-Tag"] = "noindex"

        return response
