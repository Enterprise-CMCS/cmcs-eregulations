from functools import partial

from regulations.utils import (
    STATUTE_REF_REGEX,
    USC_REF_REGEX,
    replace_sections,
    replace_usc_citations,
)

from django import template

register = template.Library()


@register.simple_tag
def link_statutes(paragraph, link_conversions, link_config):
    if link_config["link_statute_refs"]:
        paragraph = STATUTE_REF_REGEX.sub(
            partial(replace_sections, link_conversions=link_conversions, exceptions=link_config["statute_ref_exceptions"]),
            paragraph,
        )
    if link_config["link_usc_refs"]:
        paragraph = USC_REF_REGEX.sub(
            partial(replace_usc_citations, exceptions=link_config["usc_ref_exceptions"]),
            paragraph
        )
    return paragraph
