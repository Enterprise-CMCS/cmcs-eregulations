from datetime import datetime

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='version_date')
@stringfilter
def version_date(date):
    new_date = datetime.strptime(date, "%Y-%m-%d")
    return datetime.strftime(new_date, "%-m/%-d/%Y")
