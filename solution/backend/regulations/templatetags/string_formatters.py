from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_tags
from datetime import datetime

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
def simple_section_formatter(title, node_label):
    part = node_label[0]
    subpart = node_label[1]

    return strip_tags(f"{title} {part}.{subpart}")


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


@register.simple_tag
@stringfilter
def appendix_formatter(title, node_label):
    citation = " ".join(node_label)
    return strip_tags(f"{title} CFR {citation}")


@register.filter
@stringfilter
def footer_date_formatter(footer_date):
    new_date = datetime.strptime(footer_date, '%b %d, %Y')
    return new_date.strftime('%b %-d, %Y')


@register.filter
def stripSurroundingQuotes(quotedString):
    if quotedString.startswith('"') and quotedString.endswith('"'):
        return quotedString[1:-1]
    else:
        return quotedString
