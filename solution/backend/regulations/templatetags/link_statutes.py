import re

from django import template

register = template.Library()


LINK_FORMAT = '<a target="_blank" href="https://uscode.house.gov/view.xhtml'\
              '?req=granuleid:USC-prelim-title{}-section{}&num=0&edition=prelim">{}</a>'

STATUTE_REF_PATTERN = r"\bsect(?:ion[s]?|s?).?\s*((?:\d+[a-z]?(?:-+[a-z0-9]+)?(?:(?:,?\s*(?:and|or|\&)?\s*)?\([a-z0-9]+\))*"\
                      r"(?:,?\s*(?:and|or|\&)?\s*)?)+)(?:\s*of\s*the\s*([a-z0-9]*(?=\bact\b)))?"
SECTION_PATTERN = r"(\d+[a-z]?(?:-+[a-z0-9]+)?(?:(?:,?\s*(?:and|or|\&)?\s*)?\([a-z0-9]+\))*)"
SECTION_ID_PATTERN = r"(\d+[a-z]?(?:-+[a-z0-9]+)?)"

STATUTE_REF_REGEX = re.compile(STATUTE_REF_PATTERN, re.IGNORECASE)
SECTION_REGEX = re.compile(SECTION_PATTERN, re.IGNORECASE)
SECTION_ID_REGEX = re.compile(SECTION_ID_PATTERN, re.IGNORECASE)


@register.filter
def link_statutes(paragraph, link_conversions):
    def replace_section(section):
        section_text = section.group()
        section = SECTION_ID_REGEX.match(section_text).group()  # extract section
        if section in link_conversions:
            conversion = link_conversions[section]
            return LINK_FORMAT.format(conversion["title"], conversion["usc"], section_text)
        return section_text

    def replace_section_groups(match):
        # for each match, we have a string containing one or more sections and an optional associated act
        pos = match.span()
        return SECTION_REGEX.sub(replace_section, match.string[pos[0]:pos[1]])

    return STATUTE_REF_REGEX.sub(replace_section_groups, paragraph)
