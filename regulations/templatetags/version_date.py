from django import template
from django.template.defaultfilters import stringfilter
from datetime import datetime

register = template.Library()


@register.filter(name='version_date')
@stringfilter
def version_date(date):
    new_date = datetime.strptime(date, "%Y-%m-%d")
    return datetime.strftime(new_date, "%-m/%-d/%Y")
