from django import template

from resources.models import Subject

register = template.Library()

@register.simple_tag
def get_subject_id(subject_name):
    try:
        subject = Subject.objects.get(full_name=subject_name)
        return subject.id
    except Subject.DoesNotExist:
        return None
    except Exception:
        return None

