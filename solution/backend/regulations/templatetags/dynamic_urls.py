from django import template

register = template.Library()


@register.simple_tag
def get_domain(request, custom_url):
    if 'eregulations.cms.gov' in request.get_host():
        return 'https://eregulations.cms.gov/'
    else:
        return custom_url