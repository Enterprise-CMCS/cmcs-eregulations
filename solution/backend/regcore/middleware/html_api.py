import json

from django.shortcuts import render


class HtmlApi:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if "html_api" in request.GET:
            try:
                response = view_func(request, *view_args, **view_kwargs)
                data = json.dumps(response.data, indent=4)
                return render(request, "response.html", context={'data': data})
            except:
                pass
        return None
