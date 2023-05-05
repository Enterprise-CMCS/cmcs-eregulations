import re

from django import template

register = template.Library()


LINK_FORMAT = '<a target="_blank" href="https://uscode.house.gov/view.xhtml'\
              '?req=granuleid:USC-prelim-title{}-section{}&num=0&edition=prelim">{}</a>'

STATUTE_REF_PATTERN = r"\bsect(?:ion[s]?|s?).?\s*((?:\d+[a-z]?(?:-+[a-z0-9]+)?(?:(?:,?\s*(?:and|or|\&)?\s*)?\([a-z0-9]+\))*"\
                      r"(?:,?\s*(?:and|or|\&)?\s*)?)+)(?:\s*of\s*the\s*([a-z0-9]*(?=\bact\b)))?"
SECTION_PATTERN = r"(\d+[a-z]?(?:-+[a-z0-9]+)?(?:(?:,?\s*(?:and|or|\&)?\s*)?\([a-z0-9]+\))*)"
SECTION_ID_PATTERN = r"(\d+[a-z]?(?:-+[a-z0-9]+)?)"
LINKED_PARAGRAPH_PATTERN = r"((?:\([a-z0-9]+\))+)"
PARAGRAPH_PATTERN = r"\(([a-z0-9]+)\)"

statute_ref_regex = re.compile(STATUTE_REF_PATTERN, re.IGNORECASE)
section_regex = re.compile(SECTION_PATTERN, re.IGNORECASE)
section_id_regex = re.compile(SECTION_ID_PATTERN, re.IGNORECASE)
linked_paragraph_regex = re.compile(LINKED_PARAGRAPH_PATTERN, re.IGNORECASE)
paragraph_regex = re.compile(PARAGRAPH_PATTERN, re.IGNORECASE)


@register.filter
def link_statutes(paragraph, link_conversions):
    def replace_section(section):
        section_text = section.group()
        section = section_id_regex.match(section_text).group()  # extract section
        # linked_paragraphs = linked_paragraph_regex.findall(section_text)  # extract paragraph chains (e.g. (a)(1)(c)...)
        # paragraphs = [paragraph_regex.findall(p) for p in linked_paragraphs]  # extract individual paragraph items
        if section in link_conversions:
            conversion = link_conversions[section]
            return LINK_FORMAT.format(conversion["title"], conversion["usc"], section_text)
        return section_text

    def replace_section_groups(match):
        # for each match, we have a string containing one or more sections and an optional associated act
        pos = match.span()
        return section_regex.sub(replace_section, match.string[pos[0]:pos[1]])

    return statute_ref_regex.sub(replace_section_groups, paragraph)
