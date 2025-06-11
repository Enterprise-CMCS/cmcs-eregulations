from django.views.generic import TemplateView


class ManualView(TemplateView):
    template_name = "regulations/manual.html"
