from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_tags

register = template.Library()


def surround(str):
    return "(" + str + ")"


@register.simple_tag
@stringfilter
def sidebar_formatter(title, part, subpart):
    return strip_tags(f"{title} CFR Part {part}, Subpart {subpart}")


@register.simple_tag
@stringfilter
def subpart_formatter(title, citation, node_label):
    part = citation[0]
    subpart = citation[1] if len(citation) > 1 else node_label[0]

    return strip_tags(f"{title} CFR Part {part}, Subpart {subpart}")


@register.simple_tag
@stringfilter
def section_formatter(title, node_label):
    part = node_label[0]
    subpart = node_label[1]

    return strip_tags(f"{title} CFR § {part}.{subpart}")


@register.simple_tag
@stringfilter
def paragraph_formatter(title, node_label):
    part = node_label[0]
    section = node_label[1]
    subsection_list = node_label[2:]

    title_part_section = f"{title} CFR § {part}.{section}"
    return_string = title_part_section \
        if len(subsection_list[0]) > 3 \
        else title_part_section + "".join(map(surround, subsection_list))

    return strip_tags(return_string)
