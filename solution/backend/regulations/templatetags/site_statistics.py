from datetime import date

from django.template import Library

from regcore.models import Part

register = Library()


@register.simple_tag()
def last_updated():
    today = date.today()
    part = Part.objects.effective(today).first()
    if not part:
        return
    return part.last_updated.strftime("%b %d, %Y")
