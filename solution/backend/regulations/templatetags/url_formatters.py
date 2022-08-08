from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.simple_tag
@stringfilter
def ecfr_part_url_formatter(title, part):
    return f"https://www.ecfr.gov/current/title-{title}/part-{part}"
