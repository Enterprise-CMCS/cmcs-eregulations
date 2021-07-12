from datetime import date, datetime
from django.template import Library
from regulations.generator import api_reader

register = Library()
client = api_reader.ApiReader()


@register.simple_tag()
def last_updated():
    today = date.today()
    parts = client.effective_parts(today)
    try:
        return datetime.fromisoformat(parts[0]['last_updated']).date().strftime("%b %d, %Y")
    except Exception:
        return None
