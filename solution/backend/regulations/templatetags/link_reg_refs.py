import re
from functools import partial
from urllib.parse import urlencode

from django import template
from django.urls import reverse

from common.patterns import (
    CONJUNCTION_PATTERN,
    DASH_PATTERN,
    DASH_REGEX,
    LINKED_PARAGRAPH_REGEX,
    PARAGRAPH_EXTRACT_REGEX,
    PARAGRAPH_PATTERN,
    PART_SECTION_PATTERN,
    SECTION_LABEL_PATTERN,
    USC_CFR_IGNORE_PATTERN,
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
        params["paragraph"] = "-".join(params["paragraph"])
    if "section" in params:
        params["section"] = DASH_REGEX.sub("-", params["section"])
    return REDIRECT_LINK_FORMAT.format(
        reverse("reg_redirect"),
        urlencode(params),
        text,
    )
# Returns a list containing the first paragraph chain in a section ref.
# For example, if the section text is "Section 1902(a)(1)(C) and (b)(2)", this will return ["a", "1", "C"].
def extract_paragraphs(section_text):
    linked_paragraphs = LINKED_PARAGRAPH_REGEX.search(section_text)  # extract the first paragraph chain (e.g. (a)(1)(c)...)
    return PARAGRAPH_EXTRACT_REGEX.findall(linked_paragraphs.group()) if linked_paragraphs else None


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

PART_SECTION_PARAGRAPH_PATTERN = (
    rf"{PART_SECTION_PATTERN}" # Matches "123.456"
    rf"(?:(?:{CONJUNCTION_PATTERN})*({PARAGRAPH_PATTERN}))*" # Matches "and (a)" or "or (b)" at the end of the ref.
)

# Matches regulation references with paragraphs and/or additional regulation references linked with a conjunction.
# For example, "§ 123.456(a)(1)(C) and (2)" or "section 123.456 and section 789.012".
REGULATION_REF_PATTERN = (
    rf"{SECTION_LABEL_PATTERN}" # Matches "§" or "section" or "sections"
    rf"{PART_SECTION_PARAGRAPH_PATTERN}"
    rf"(?:{CONJUNCTION_PATTERN}{PART_SECTION_PATTERN})*" # Matches any number of "and 123.789" or "or 456.012" at the end
)

REGULATION_REF_EXTRACT_PATTERN = (
    rf"{PART_SECTION_PARAGRAPH_PATTERN}"
    rf"(?:{CONJUNCTION_PATTERN}{PART_SECTION_PATTERN})*" # Matches any number of "and 123.789" or "or 456.012" at the end
)

PART_SECTION_PARAGRAPH_REGEX = re.compile(PART_SECTION_PARAGRAPH_PATTERN, re.IGNORECASE)
REGULATION_REF_REGEX = re.compile(REGULATION_REF_PATTERN, re.IGNORECASE)
REGULATION_REF_EXTRACT_REGEX = re.compile(REGULATION_REF_EXTRACT_PATTERN, re.IGNORECASE)

def replace_regulation_ref(match, title, exceptions={}):
    return REGULATION_REF_EXTRACT_REGEX.sub(
        partial(replace_cfr_ref, title=title, exceptions=exceptions.get(42, [])),
        match.group()
    )

# This function is run by re.sub() to replace regulation refs in "123.456" format with links.
def replace_regulation_refs(match, link_conversions=[], exceptions={}):
    title = 42
    return PART_SECTION_PARAGRAPH_REGEX.sub(
        partial(replace_regulation_ref, title=title, exceptions=exceptions),
        match.group()
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
