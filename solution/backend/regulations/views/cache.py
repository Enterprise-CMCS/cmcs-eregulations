from django.views.generic.base import TemplateView


class CacheView(TemplateView):

    template_name = 'regulations/cache.html'
