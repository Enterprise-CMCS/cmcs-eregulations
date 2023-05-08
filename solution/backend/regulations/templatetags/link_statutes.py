from functools import partial
import re

from django import template

register = template.Library()


LINK_FORMAT = '<a target="_blank" href="https://uscode.house.gov/view.xhtml'\
              '?req=granuleid:USC-prelim-title{}-section{}&num=0&edition=prelim">{}</a>'

STATUTE_REF_PATTERN = r"\bsect(?:ion[s]?|s?).?\s*((?:\d+[a-z]?(?:-+[a-z0-9]+)?(?:(?:,?\s*(?:and|or|\&)?\s*)?\([a-z0-9]+\))*"\
                      r"(?:,?\s*(?:and|or|\&)?\s*)?)+)(?:\s*of\s*the\s*([a-z0-9\s]*?(?=\bact\b)))?"
SECTION_PATTERN = r"(\d+[a-z]?(?:-+[a-z0-9]+)?(?:(?:,?\s*(?:and|or|\&)?\s*)?\([a-z0-9]+\))*)"
SECTION_ID_PATTERN = r"(\d+[a-z]?(?:-+[a-z0-9]+)?)"

STATUTE_REF_REGEX = re.compile(STATUTE_REF_PATTERN, re.IGNORECASE)
SECTION_REGEX = re.compile(SECTION_PATTERN, re.IGNORECASE)
SECTION_ID_REGEX = re.compile(SECTION_ID_PATTERN, re.IGNORECASE)

DEFAULT_ACT = "Social Security Act"


def replace_section(section, act, link_conversions):
    section_text = section.group()
    section = SECTION_ID_REGEX.match(section_text).group()  # extract section
    act = f"{act.strip()} Act" if act else DEFAULT_ACT  # if no act is specified, default to DEFAULT_ACT
    if act in link_conversions and section in link_conversions[act]:
        conversion = link_conversions[act][section]
        return LINK_FORMAT.format(conversion["title"], conversion["usc"], section_text)
    return section_text


def replace_section_groups(match, link_conversions):
    return SECTION_REGEX.sub(
        partial(replace_section, act=match.group(2), link_conversions=link_conversions),
        match.group(),
    )


@register.filter
def link_statutes(paragraph, link_conversions):
    return STATUTE_REF_REGEX.sub(
        partial(replace_section_groups, link_conversions=link_conversions),
        paragraph,
    )
