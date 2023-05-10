import re
from functools import partial

from django import template

register = template.Library()


LINK_FORMAT = '<a target="_blank" class="external" href="https://uscode.house.gov/view.xhtml'\
              '?req=granuleid:USC-prelim-title{}-section{}&num=0&edition=prelim">{}</a>'

# Extracts the section ID only, for example "1902-1G" and its variations.
SECTION_ID_PATTERN = r"\d+[a-z]?(?:-+[a-z0-9]+)?"

# Matches ", and", ", or", "and", "or", "&", and more variations.
AND_OR_PATTERN = r"(?:,?\s*(?:and|or|\&)?\s*)?"

# Matches individual sections, for example "Section 1902(a)(2) and (b)(1)" and its variations.
SECTION_PATTERN = rf"{SECTION_ID_PATTERN}(?:{AND_OR_PATTERN}\([a-z0-9]+\))*"

# Matches entire statute references, including one or more sections and an optional Act.
# For example, "Sections 1902(a)(2) and (b)(1) and 1903(b) of the Social Security Act" and its variations.
# Will also match "Section 1902" if the section is contained within the DEFAULT_ACT. See tests for more complete examples.
STATUTE_REF_PATTERN = rf"\bsect(?:ion[s]?|s?).?\s*((?:{SECTION_PATTERN}{AND_OR_PATTERN})+)"\
                      r"(?:\s*of\s*the\s*([a-z0-9\s]*?(?=\bact\b)))?"

# Regex's are precompiled to improve page load time.
SECTION_ID_REGEX = re.compile(rf"({SECTION_ID_PATTERN})", re.IGNORECASE)
SECTION_REGEX = re.compile(rf"({SECTION_PATTERN})", re.IGNORECASE)
STATUTE_REF_REGEX = re.compile(STATUTE_REF_PATTERN, re.IGNORECASE)

# The act to use if none is specified, for example "section 1902 of the act" defaults to this.
DEFAULT_ACT = "Social Security Act"


# This function is run by re.sub() to replace individual section refs with links.
# "act" and "link_conversions" must be passed in via a partial function.
def replace_section(section, act, link_conversions):
    section_text = section.group()
    section = SECTION_ID_REGEX.match(section_text).group()  # extract section
    act = f"{act.strip()} Act" if act else DEFAULT_ACT  # if no act is specified, default to DEFAULT_ACT
    if act in link_conversions and section in link_conversions[act]:
        # only link if section exists within the relevant act
        conversion = link_conversions[act][section]
        return LINK_FORMAT.format(conversion["title"], conversion["usc"], section_text)
    return section_text


# This middleman re.sub() function is run when an entire statute ref is matched. It performs another substition on individual
# sections within the ref. It is needed to enforce refs starting with "section" but possibly containing more than one section.
# "link_conversions" must be passed in via a partial function.
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
