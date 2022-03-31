import json

from django.shortcuts import render


class HtmlApi:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "html_api" in request.GET and response.get("Content-Type", None) == "application/json":
            data = json.dumps(json.loads(response.content.decode("utf-8")), indent=4)
            return render(request, "response.html", context={'data': data})
        return response
