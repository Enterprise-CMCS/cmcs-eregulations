from django.views.generic.base import TemplateView


class ResourcesView(TemplateView):
    template_name = 'regulations/resources.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c = {
            'hide_resource_btn': True,
        }

        return {**context, **c}
