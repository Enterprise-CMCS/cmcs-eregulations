from django import template

register = template.Library()
section_depth = 2


@register.filter(name='pdepth')
def pdepth(value):
    label_len = len(value.get("label", []) or [])
    marker_len = len(value.get("marker", []) or [])
    depth = label_len - section_depth

    if label_len == 0:
        return 1
    elif marker_len > 1:
        return depth - (marker_len - 1)
    else:
        return depth
