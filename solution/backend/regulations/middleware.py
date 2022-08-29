import json
import traceback

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
