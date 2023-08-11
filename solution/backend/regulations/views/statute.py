from django.views.generic.base import TemplateView

from regulations.models import (
    SiteConfiguration,
)

class StatuteView(TemplateView):
    template_name = 'regulations/statute.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = self.request.get_host()
        site_config = SiteConfiguration.get_solo()
        site_config = {
            'us_code_house_gov': {
                'type': site_config.us_code_house_gov_date_type,
                'date': site_config.us_code_house_gov_date,
            },
            'us_code_annual': {
                'type': site_config.us_code_annual_date_type,
                'date': site_config.us_code_annual_date,
            },
            'statute_compilation': {
                'type': site_config.statute_compilation_date_type,
                'date': site_config.statute_compilation_date,
            },
            'ssa_gov_compilation': {
                'type': site_config.ssa_gov_compilation_date_type,
                'date': site_config.ssa_gov_compilation_date,
            },
        }

        c = {
            'host': host,
            'site_config': site_config,
         }

        return {**context, **c, **self.request.GET.dict()}
