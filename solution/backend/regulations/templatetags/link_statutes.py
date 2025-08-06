from functools import partial

from django import template

from regulations.utils import (
    REGULATION_REF_REGEX,
    STATUTE_REF_REGEX,
    USC_REF_REGEX,
    replace_regulation_ref,
    replace_sections,
    replace_usc_citations,
)

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

    paragraph = REGULATION_REF_REGEX.sub(
        partial(replace_regulation_ref),
        paragraph,
    )

    return paragraph
