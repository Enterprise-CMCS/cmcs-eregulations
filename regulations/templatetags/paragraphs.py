from django import template

register = template.Library()
section_depth = 2


@register.filter(name='pdepth')
def pdepth(value):
    if value.get("parent_type", "") == "appendix":
        return 1
    else:
        depth = len(value.get("label", []) or []) - section_depth
        if len(value.get("marker", []) or []) > 1:
            depth = depth - (len(value.get("marker", []) or []) - 1)
        return depth
