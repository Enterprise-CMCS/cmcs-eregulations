from django import template

register = template.Library()
section_depth = 2


@register.filter(name='pdepth')
def pdepth(value):
    parent_type = value.get("parent_type", "")
    label_len = len(value.get("label", []))
    marker_len = len(value.get("marker", []) or [])
    depth = label_len - section_depth

    if parent_type == "appendix" or label_len == 0:
        return 1
    elif marker_len > 1:
        return depth - (marker_len - 1)
    else:
        return depth
