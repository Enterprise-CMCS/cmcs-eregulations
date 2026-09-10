from django.template import Library

from regcore.models import Part

register = Library()


@register.simple_tag()
def last_updated():
    part = Part.objects.order_by("title", "name").first()
    if not part:
        return
    return part.last_updated.strftime("%b %d, %Y")
