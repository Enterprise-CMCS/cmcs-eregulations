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


class JsonErrors:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if "json_errors" in request.GET:
            error = {
                "status": "error",
                "type": str(type(exception)),
                "exception": str(exception),
                "traceback": traceback.extract_tb(exception.__traceback__).format(),
            }

            return HttpResponse(json.dumps(error), content_type="application/json", status=500)
        else:
            return None


_site_uri = None


def get_site_uri():
    global _site_uri
    return _site_uri


class SiteUriMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _site_uri
        _site_uri = request.build_absolute_uri("/")
        return self.get_response(request)
