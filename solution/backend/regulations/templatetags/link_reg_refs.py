import re
from functools import partial
from urllib.parse import urlencode

from django import template
from django.urls import reverse

from common.patterns import (
    CONJUNCTION_PATTERN,
    DASH_REGEX,
    PARAGRAPH_PATTERN,
    SECTION_ID_PATTERN,
    SECTION_LABEL_PATTERN,
    USC_CFR_IGNORE_PATTERN,
)
from regulations.utils import (
    extract_paragraphs,
)

register = template.Library()


REDIRECT_LINK_FORMAT = '<a target="_blank" rel="noopener noreferrer" href="{}?{}">{}</a>'

CFR_REF_EXTRACT_PATTERN = rf"(\d+)(?:\.({SECTION_ID_PATTERN})((?:{PARAGRAPH_PATTERN})*))?"
CFR_REF_PATTERN = rf"\d+(?:\.{SECTION_ID_PATTERN}(?:{PARAGRAPH_PATTERN})*)?"
CFR_PATTERN = rf"(\d+)\s*c.?f.?r.?\s*(?:parts?\s*)?((?:{CFR_REF_PATTERN}{CONJUNCTION_PATTERN}(?!{USC_CFR_IGNORE_PATTERN}))+)"

CFR_REF_EXTRACT_REGEX = re.compile(CFR_REF_EXTRACT_PATTERN, re.IGNORECASE)
CFR_REGEX = re.compile(CFR_PATTERN, re.IGNORECASE)


def create_redirect_link(text, *args, **kwargs):
    params = {i: kwargs[i] for i in kwargs if kwargs[i]}
    if "paragraph" in params:
        params["paragraph"] = "-".join(params["paragraph"])
    if "section" in params:
        params["section"] = DASH_REGEX.sub("-", params["section"])
    return REDIRECT_LINK_FORMAT.format(
        reverse("reg_redirect"),
        urlencode(params),
        text,
    )


def replace_cfr_ref(match, title, exceptions):
    match_text = match.group()
    if DASH_REGEX.sub("-", match.group()) in exceptions:
        return match.group()
    return create_redirect_link(
        match.group(),
        title=title,
        part=match.group(1),
        section=match.group(2),
        paragraph=extract_paragraphs(match_text) or None,
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


# Matches part.section format, for example "123.456" or "123(a)(1)".
# These need to be grouped for use in replace_cfr_ref() for part/section extraction.
GROUPED_PART_SECTION_PATTERN = rf"({SECTION_ID_PATTERN})\.({SECTION_ID_PATTERN})"

PART_SECTION_PARAGRAPH_PATTERN = (
    rf"{GROUPED_PART_SECTION_PATTERN}"  # Matches "123.456"
    rf"(?:(?:{CONJUNCTION_PATTERN})*({PARAGRAPH_PATTERN}))*"  # Matches "and (a)" or "or (b)" at the end of the ref.
)

# Matches regulation references with paragraphs and/or additional regulation references linked with a conjunction.
# For example, "§ 123.456(a)(1)(C) and (2)" or "section 123.456 and section 789.012".
REGULATION_REF_PATTERN = (
    rf"{SECTION_LABEL_PATTERN}"  # Matches "§" or "section" or "sections"
    rf"{PART_SECTION_PARAGRAPH_PATTERN}"
    rf"(?:{CONJUNCTION_PATTERN}{GROUPED_PART_SECTION_PATTERN})*"  # Matches any number of "and 123.789" or "or 456.012" at the end
)

REGULATION_REF_EXTRACT_PATTERN = (
    rf"{PART_SECTION_PARAGRAPH_PATTERN}"
    rf"(?:{CONJUNCTION_PATTERN}{GROUPED_PART_SECTION_PATTERN})*"  # Matches any number of "and 123.789" or "or 456.012" at the end
)

PART_SECTION_PARAGRAPH_REGEX = re.compile(PART_SECTION_PARAGRAPH_PATTERN, re.IGNORECASE)
REGULATION_REF_REGEX = re.compile(REGULATION_REF_PATTERN, re.IGNORECASE)
REGULATION_REF_EXTRACT_REGEX = re.compile(REGULATION_REF_EXTRACT_PATTERN, re.IGNORECASE)


def replace_regulation_ref(match, title, exceptions={}):
    return REGULATION_REF_EXTRACT_REGEX.sub(
        partial(replace_cfr_ref, title=title, exceptions=exceptions.get(title, [])),
        match.group()
    )


# This function is run by re.sub() to replace regulation refs in "123.456" format with links.
def replace_regulation_refs(match, title, link_conversions=[], exceptions={}):
    return PART_SECTION_PARAGRAPH_REGEX.sub(
        partial(replace_regulation_ref, title=title, exceptions=exceptions),
        match.group()
    )

PART_PATTERN = rf"(\s*part\s*?\b{SECTION_ID_PATTERN}\b)"
PART_CHILD_PATTERN = r"(?:\s*\b(?:sub)?(?:part|chapter)\b\s*?[A-Za-z0-9]+)?"
OF_THIS_PATTERN = r"\s*(?:\s*of\s*this\s*?\b(?:sub)?(?:chapter|title)\b)"
PART_OF_THIS_PATTERN = rf"{PART_PATTERN}(?=,?{PART_CHILD_PATTERN},?{OF_THIS_PATTERN})"
SECTION_EXTRACT_PATTERN = rf"({SECTION_ID_PATTERN})"

PART_OF_THIS_REGEX = re.compile(PART_OF_THIS_PATTERN, re.IGNORECASE)
SECTION_EXTRACT_REGEX = re.compile(SECTION_EXTRACT_PATTERN, re.IGNORECASE)


def replace_part_of(match, title, exceptions={}):
    if DASH_REGEX.sub("-", match.group()) in exceptions:
        return match.group()
    return create_redirect_link(
        match.group(),
        title=title,
        part=match.group(1)
    )

def replace_part_ofs(match, title, exceptions={}):
    return SECTION_EXTRACT_REGEX.sub(
        partial(replace_part_of, title=title, exceptions=exceptions.get(title, [])),
        match.group()
    )


@register.simple_tag
def link_reg_refs(paragraph, link_config, title=None):
    if link_config["link_cfr_refs"]:
        paragraph = CFR_REGEX.sub(
            partial(replace_cfr_refs, exceptions=link_config["cfr_ref_exceptions"]),
            paragraph,
        )
        paragraph = REGULATION_REF_REGEX.sub(
            partial(replace_regulation_refs, title=title, exceptions=link_config["cfr_ref_exceptions"]),
            paragraph,
        )
        paragraph = PART_OF_THIS_REGEX.sub(
            partial(replace_part_ofs, title=title, exceptions=link_config["cfr_ref_exceptions"]),
            paragraph,
        )
    return paragraph
