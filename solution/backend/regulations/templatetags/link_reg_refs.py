import re
from functools import partial
from urllib.parse import urlencode

from django import template

from common.patterns import (
    AND_OR_PATTERN,
    DASH_PATTERN,
    DASH_REGEX,
    PARAGRAPH_EXTRACT_REGEX,
    PARAGRAPH_PATTERN,
    USC_CFR_IGNORE_PATTERN,
)

register = template.Library()


REDIRECT_LINK_FORMAT = '<a target="blank" href="/reg_redirect?{}">{}</a>'

SECTION_PATTERN = rf"\d+[a-z]*(?:(?:{DASH_PATTERN})+[a-z0-9]+)?"
CFR_REF_EXTRACT_PATTERN = rf"(\d+)(?:\.({SECTION_PATTERN})((?:{PARAGRAPH_PATTERN})*))?"
CFR_REF_PATTERN = rf"\d+(?:\.{SECTION_PATTERN}(?:{PARAGRAPH_PATTERN})*)?"
CFR_PATTERN = rf"(\d+)\s*c.?f.?r.?\s*(?:parts?\s*)?((?:{CFR_REF_PATTERN}{AND_OR_PATTERN}(?!{USC_CFR_IGNORE_PATTERN}))+)"

CFR_REF_EXTRACT_REGEX = re.compile(CFR_REF_EXTRACT_PATTERN, re.IGNORECASE)
CFR_REGEX = re.compile(CFR_PATTERN, re.IGNORECASE)


def create_redirect_link(text, *args, **kwargs):
    params = {i: kwargs[i] for i in kwargs if kwargs[i]}
    if "paragraph" in params:
        params["paragraph"] = ".".join(PARAGRAPH_EXTRACT_REGEX.findall(params["paragraph"]))
    if "section" in params:
        params["section"] = DASH_REGEX.sub("-", params["section"])
    return REDIRECT_LINK_FORMAT.format(
        urlencode(params),
        text,
    )


def replace_cfr_ref(match, title):
    return create_redirect_link(
        match.group(),
        title=title,
        part=match.group(1),
        section=match.group(2),
        paragraph=match.group(3),
    )


def replace_cfr_refs(match):
    title = match.group(1)
    refs = match.group(2)
    return match.group().replace(
        refs,
        CFR_REF_EXTRACT_REGEX.sub(
            partial(replace_cfr_ref, title=title),
            refs
        )
    )


@register.simple_tag
def link_reg_refs(paragraph, link_config):
    paragraph = CFR_REGEX.sub(replace_cfr_refs, paragraph)
    return paragraph
