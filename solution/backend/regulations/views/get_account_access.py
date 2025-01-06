from django.views.generic.base import TemplateView


class GetAccountAccessView(TemplateView):

    template_name = 'regulations/get_account_access.html'
