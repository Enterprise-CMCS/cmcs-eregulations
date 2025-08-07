import re
from functools import partial
from urllib.parse import urlencode

from django import template
from django.urls import reverse

from common.patterns import (
    CONJUNCTION_PATTERN,
    DASH_PATTERN,
    DASH_REGEX,
    PARAGRAPH_EXTRACT_REGEX,
    PARAGRAPH_PATTERN,
    USC_CFR_IGNORE_PATTERN,
)
from regulations.utils import (
    REGULATION_REF_REGEX,
    replace_regulation_refs,
)

register = template.Library()


REDIRECT_LINK_FORMAT = '<a target="_blank" rel="noopener noreferrer" href="{}?{}">{}</a>'

SECTION_PATTERN = rf"\d+[a-z]*(?:(?:{DASH_PATTERN})+[a-z0-9]+)?"
CFR_REF_EXTRACT_PATTERN = rf"(\d+)(?:\.({SECTION_PATTERN})((?:{PARAGRAPH_PATTERN})*))?"
CFR_REF_PATTERN = rf"\d+(?:\.{SECTION_PATTERN}(?:{PARAGRAPH_PATTERN})*)?"
CFR_PATTERN = rf"(\d+)\s*c.?f.?r.?\s*(?:parts?\s*)?((?:{CFR_REF_PATTERN}{CONJUNCTION_PATTERN}(?!{USC_CFR_IGNORE_PATTERN}))+)"

CFR_REF_EXTRACT_REGEX = re.compile(CFR_REF_EXTRACT_PATTERN, re.IGNORECASE)
CFR_REGEX = re.compile(CFR_PATTERN, re.IGNORECASE)


def create_redirect_link(text, *args, **kwargs):
    params = {i: kwargs[i] for i in kwargs if kwargs[i]}
    if "paragraph" in params:
        params["paragraph"] = "-".join(PARAGRAPH_EXTRACT_REGEX.findall(params["paragraph"]))
    if "section" in params:
        params["section"] = DASH_REGEX.sub("-", params["section"])
    return REDIRECT_LINK_FORMAT.format(
        reverse("reg_redirect"),
        urlencode(params),
        text,
    )


def replace_cfr_ref(match, title, exceptions):
    if DASH_REGEX.sub("-", match.group()) in exceptions:
        return match.group()
    return create_redirect_link(
        match.group(),
        title=title,
        part=match.group(1),
        section=match.group(2),
        paragraph=match.group(3),
    )


def replace_cfr_refs(match, exceptions):
    title = match.group(1)
    refs = match.group(2)
    return match.group().replace(
        refs,
        CFR_REF_EXTRACT_REGEX.sub(
            partial(replace_cfr_ref, title=title, exceptions=exceptions.get(title, [])),
            refs,
        )
    )


@register.simple_tag
def link_reg_refs(paragraph, link_config):
    if link_config["link_cfr_refs"]:
        paragraph = CFR_REGEX.sub(
            partial(replace_cfr_refs, exceptions=link_config["cfr_ref_exceptions"]),
            paragraph,
        )
        paragraph = REGULATION_REF_REGEX.sub(
                partial(replace_regulation_refs, exceptions=link_config["cfr_ref_exceptions"]),
            paragraph,
        )
    return paragraph
