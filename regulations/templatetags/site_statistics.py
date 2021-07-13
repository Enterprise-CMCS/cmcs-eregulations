from datetime import date, datetime
from django.template import Library

from regcore.models import Part

register = Library()


@register.simple_tag()
def last_updated():
    today = date.today()
    parts = Part.objects.effective(today)
    try:
        return datetime.fromisoformat(parts[0]['last_updated']).date().strftime("%b %d, %Y")
    except Exception:
        return None
