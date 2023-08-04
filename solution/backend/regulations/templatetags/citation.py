import re

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

el = ('<a href="https://federalregister.gov/citation/', '" target="_blank" rel="noopener noreferrer">', '</a>')


@register.filter(name='citation', needs_autoescape=True, is_safe=True)
@stringfilter
def citation(citation, autoescape=True):
    if autoescape:
        citation = conditional_escape(citation)
    citation = linkify(citation)

    return mark_safe(citation)  # nosec # noqa: S308


def linkify(citation):
    final_rules = re.findall(r"\d{2} FR \d+", citation)

    for fr in final_rules:
        fr_url = "-".join(fr.split(" "))
        url = f'{el[0]}{fr_url}{el[1]}{fr}{el[2]}'
        citation = citation.replace(fr, url)
    return citation
