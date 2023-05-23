import re
from functools import partial

from django import template

register = template.Library()


USCODE_LINK_FORMAT = '<a target="_blank" class="external" href="https://uscode.house.gov/view.xhtml'\
                     '?req=granuleid:USC-prelim-title{}-section{}&num=0&edition=prelim{}">{}</a>'
USCODE_SUBSTRUCT_FORMAT = "#substructure-location_{}"

# Extracts the section ID only, for example "1902-1G" and its variations.
SECTION_ID_PATTERN = r"\d+[a-z]*(?:[—–-]+[a-z0-9]+)?"

# Matches ", and", ", or", "and", "or", "&", and more variations.
AND_OR_PATTERN = r"(?:,?\s*(?:and|or|\&)?\s*)?"

# Extracts a paragraph identifier (e.g. (a) extracts "a").
PARAGRAPH_PATTERN = r"\(([a-z0-9]+)\)"

# Matches individual sections, for example "1902(a)(2) and (b)(1)" and its variations.
SECTION_PATTERN = rf"{SECTION_ID_PATTERN}(?:{AND_OR_PATTERN}\([a-z0-9]+\))*"

# Matches entire statute references, including one or more sections and an optional Act.
# For example, "Sections 1902(a)(2) and (b)(1) and 1903(b) of the Social Security Act" and its variations.
# Will also match "Section 1902" if the section is contained within the DEFAULT_ACT. See tests for more complete examples.
STATUTE_REF_PATTERN = rf"\bsect(?:ion[s]?|s?)\.?\s*((?:{SECTION_PATTERN}{AND_OR_PATTERN})+)"\
                      r"(?:\s*of\s*the\s*([a-z0-9\s]*?(?=\bact\b)))?"

# Regex's are precompiled to improve page load time.
SECTION_ID_REGEX = re.compile(rf"({SECTION_ID_PATTERN})", re.IGNORECASE)
SECTION_REGEX = re.compile(rf"({SECTION_PATTERN})", re.IGNORECASE)
STATUTE_REF_REGEX = re.compile(STATUTE_REF_PATTERN, re.IGNORECASE)
PARAGRAPH_REGEX = re.compile(PARAGRAPH_PATTERN, re.IGNORECASE)

# The act to use if none is specified, for example "section 1902 of the act" defaults to this.
DEFAULT_ACT = "Social Security Act"


# Returns the first paragraph identifier in the section.
# For example, if the section text is "Section 1902(a)(1)(C) and (b)(2)", this will return "a".
def extract_paragraph(section_text):
    match = PARAGRAPH_REGEX.search(section_text)
    return match.group(1) if match else None


# This function is run by re.sub() to replace individual section refs with links.
# "act" and "link_conversions" must be passed in via a partial function.
def replace_section(section, act, link_conversions):
    section_text = section.group()
    section = SECTION_ID_REGEX.match(section_text).group()  # extract section
    # only link if section exists within the relevant act
    if act in link_conversions and section in link_conversions[act]:
        paragraph = extract_paragraph(section_text)
        conversion = link_conversions[act][section]
        return USCODE_LINK_FORMAT.format(
            conversion["title"],
            conversion["usc"],
            USCODE_SUBSTRUCT_FORMAT.format(paragraph) if paragraph else "",
            section_text,
        )
    return section_text


# This middleman re.sub() function is run when an entire statute ref is matched. It performs another substition on individual
# sections within the ref. It is needed to enforce refs starting with "section" but possibly containing more than one section.
# "link_conversions" must be passed in via a partial function.
def replace_sections(match, link_conversions):
    act = match.group(2)
    act = f"{act.strip()} Act" if act else DEFAULT_ACT  # if no act is specified, default to DEFAULT_ACT
    return SECTION_REGEX.sub(
        partial(replace_section, act=act, link_conversions=link_conversions),
        match.group(),
    )


# This pattern matches USC citations such as "42 U.S.C. 1901(a)", "42 U.S.C. 1901(a) or (b)",
# "42 U.S.C. 1901(a) and 1902(b)" and more variations, similar to STATUTE_REF_PATTERN.
# Negative lookahead ensures "42 U.S.C. 1234 and 41 U.S.C. 4567" doesn't register "1234" and "41" as two sections in one ref.
USC_PATTERN = r"\s*u.?\s*s.?\s*c.?\s*"
USC_REF_PATTERN = rf"(\d+){USC_PATTERN}((?:{SECTION_PATTERN}{AND_OR_PATTERN}(?!\d+{USC_PATTERN}))+)"
USC_REF_REGEX = re.compile(USC_REF_PATTERN, re.IGNORECASE)


# Replaces individual USC refs with links, to be run by re.sub().
# "title" must be passed in via a partial function.
def replace_usc_citation(match, title):
    citation_text = match.group()
    section = SECTION_ID_REGEX.match(citation_text).group()
    return USCODE_LINK_FORMAT.format(title, section, "", citation_text)


# Matches entire USC citations to account for "and", "or" scenarios.
def replace_usc_citations(match):
    return match.group().replace(
        match.group(2),
        SECTION_REGEX.sub(
            partial(replace_usc_citation, title=match.group(1)),
            match.group(2),
        )
    )


@register.filter
def link_statutes(paragraph, link_conversions):
    paragraph = STATUTE_REF_REGEX.sub(
        partial(replace_sections, link_conversions=link_conversions),
        paragraph,
    )
    paragraph = USC_REF_REGEX.sub(replace_usc_citations, paragraph)
    return paragraph
