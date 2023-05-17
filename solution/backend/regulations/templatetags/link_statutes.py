import re
from functools import partial

from django import template

register = template.Library()


USCODE_LINK_FORMAT = '<a target="_blank" class="external" href="https://uscode.house.gov/view.xhtml'\
                     '?req=granuleid:USC-prelim-title{}-section{}&num=0&edition=prelim{}">{}</a>'
USCODE_SUBSTRUCT_FORMAT = "#substructure-location_{}"

# Extracts the section ID only, for example "1902-1G" and its variations.
SECTION_ID_PATTERN = r"\d+[a-z]?(?:-+[a-z0-9]+)?"

# Matches ", and", ", or", "and", "or", "&", and more variations.
AND_OR_PATTERN = r"(?:,?\s*(?:and|or|\&)?\s*)?"

# Matches individual sections, for example "Section 1902(a)(2) and (b)(1)" and its variations.
SECTION_PATTERN = rf"{SECTION_ID_PATTERN}(?:{AND_OR_PATTERN}\([a-z0-9]+\))*"

# Matches entire statute references, including one or more sections and an optional Act.
# For example, "Sections 1902(a)(2) and (b)(1) and 1903(b) of the Social Security Act" and its variations.
# Will also match "Section 1902" if the section is contained within the DEFAULT_ACT. See tests for more complete examples.
STATUTE_REF_PATTERN = rf"\bsect(?:ion[s]?|s?)\.?\s*((?:{SECTION_PATTERN}{AND_OR_PATTERN})+)"\
                      r"(?:\s*of\s*the\s*([a-z0-9\s]*?(?=\bact\b)))?"

# Matches chains of paragraphs, for example in "Section 1902(a)(1)(C)", "(a)(1)(C)" will match.
LINKED_PARAGRAPH_PATTERN = r"((?:\([a-z0-9]+\))+)"

# Extracts paragraph identifiers. Running findall() on "(a)(1)(C)" returns ["a", "1", "C"].
PARAGRAPH_PATTERN = r"\(([a-z0-9]+)\)"

# Regex's are precompiled to improve page load time.
SECTION_ID_REGEX = re.compile(rf"({SECTION_ID_PATTERN})", re.IGNORECASE)
SECTION_REGEX = re.compile(rf"({SECTION_PATTERN})", re.IGNORECASE)
STATUTE_REF_REGEX = re.compile(STATUTE_REF_PATTERN, re.IGNORECASE)
LINKED_PARAGRAPH_REGEX = re.compile(LINKED_PARAGRAPH_PATTERN, re.IGNORECASE)
PARAGRAPH_REGEX = re.compile(PARAGRAPH_PATTERN, re.IGNORECASE)

# The act to use if none is specified, for example "section 1902 of the act" defaults to this.
DEFAULT_ACT = "Social Security Act"


# Returns a list containing the first paragraph chain in a section ref.
# For example, if the section text is "Section 1902(a)(1)(C) and (b)(2)", this will return ["a", "1", "C"].
def extract_paragraphs(section_text):
    linked_paragraphs = LINKED_PARAGRAPH_REGEX.search(section_text)  # extract the first paragraph chain (e.g. (a)(1)(c)...)
    return PARAGRAPH_REGEX.findall(linked_paragraphs.group()) if linked_paragraphs else None


# This function is run by re.sub() to replace individual section refs with links.
# "act" and "link_conversions" must be passed in via a partial function.
def replace_section(section, act, link_conversions):
    section_text = section.group()
    section = SECTION_ID_REGEX.match(section_text).group()  # extract section
    # only link if section exists within the relevant act
    if act in link_conversions and section in link_conversions[act]:
        paragraphs = extract_paragraphs(section_text)
        conversion = link_conversions[act][section]
        return USCODE_LINK_FORMAT.format(
            conversion["title"],
            conversion["usc"],
            USCODE_SUBSTRUCT_FORMAT.format("_".join(paragraphs)) if paragraphs else "",
            section_text,
        )
    return section_text


# This middleman re.sub() function is run when an entire statute ref is matched. It performs another substition on individual
# sections within the ref. It is needed to enforce refs starting with "section" but possibly containing more than one section.
# "link_conversions" must be passed in via a partial function.
def replace_section_groups(match, link_conversions):
    act = match.group(2)
    act = f"{act.strip()} Act" if act else DEFAULT_ACT  # if no act is specified, default to DEFAULT_ACT
    return SECTION_REGEX.sub(
        partial(replace_section, act=act, link_conversions=link_conversions),
        match.group(),
    )


@register.filter
def link_statutes(paragraph, link_conversions):
    return STATUTE_REF_REGEX.sub(
        partial(replace_section_groups, link_conversions=link_conversions),
        paragraph,
    )
