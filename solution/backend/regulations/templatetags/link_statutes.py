import re
from functools import partial

from django import template

register = template.Library()


USCODE_LINK_FORMAT = '<a target="_blank" class="external" href="https://uscode.house.gov/view.xhtml'\
                     '?req=granuleid:USC-prelim-title{}-section{}&num=0&edition=prelim{}">{}</a>'
USCODE_SUBSTRUCT_FORMAT = "#substructure-location_{}"

DASH_PATTERN = r"[-—–-–]|&#x2013;"

NUMBER_PATTERN = r"[0-9]+"

# Extracts the section ID only, for example "1902-1G" and its variations.
SECTION_ID_PATTERN = rf"\d+[a-z]*(?:(?:{DASH_PATTERN})+[a-z0-9]+)?"

# Matches ", and", ", or", "and", "or", "&", and more variations.
AND_OR_PATTERN = r"(?:,?\s*(?:and|or|\&)?\s*)?"

# Extracts a paragraph identifier (e.g. (a) extracts "a").
PARAGRAPH_PATTERN = r"\(([a-z0-9]+)\)"

# Matches individual sections, for example "1902(a)(2) and (b)(1)" and its variations.
SECTION_PATTERN = rf"{SECTION_ID_PATTERN}(?:{AND_OR_PATTERN}\([a-z0-9]+\))*"

# Matches entire statute references, including one or more sections and an optional Act.
# For example, "Sections 1902(a)(2) and (b)(1) and 1903(b) of the Social Security Act" and its variations.
# Will also match "Section 1902" if the section is contained within the DEFAULT_ACT. See tests for more complete examples.
STATUTE_REF_PATTERN = rf"(?:\bsec(?:tions?|t?s?)?|§|&#xA7;)\.?\s*((?:{SECTION_PATTERN}{AND_OR_PATTERN})+)"\
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
DASH_REGEX = re.compile(DASH_PATTERN, re.IGNORECASE)
NUMBER_REGEX = re.compile(NUMBER_PATTERN, re.IGNORECASE)

# The act to use if none is specified, for example "section 1902 of the act" defaults to this.
DEFAULT_ACT = "Social Security Act"


# This takes a section identifier and tries to determine if a dash within it is part of the ID, or marking continuity.
# We assume that all section IDs start with a number. So we can extract the numeric parts and, if B >= A, we can conclude that
# it's continuity, e.g. "section 1000A-1003B" means "1000A through 1003B", versus "1000A-1G" where "1G" is part of the ID.
# Returns ("A", "-B") if it's continuation, or ("A", "") otherwise. Raises ValueError if section starts without a number.
def split_citation(citation):
    dash = DASH_REGEX.search(citation)
    if not dash:
        return citation, ""
    # First part of a citation is always numeric, so compare numeric parts to determine continuity
    split = DASH_REGEX.split(citation, maxsplit=1)
    a, b = [NUMBER_REGEX.match(i) for i in split]
    if not a:
        raise ValueError
    if not b or int(b.group()) < int(a.group()):
        return citation, ""
    return split[0], dash.group() + split[1]


# Returns a list containing the first paragraph chain in a section ref.
# For example, if the section text is "Section 1902(a)(1)(C) and (b)(2)", this will return ["a", "1", "C"].
def extract_paragraphs(section_text):
    linked_paragraphs = LINKED_PARAGRAPH_REGEX.search(section_text)  # extract the first paragraph chain (e.g. (a)(1)(c)...)
    return PARAGRAPH_REGEX.findall(linked_paragraphs.group()) if linked_paragraphs else None


# This function is run by re.sub() to replace individual section refs with links.
# "act" and "link_conversions" must be passed in via a partial function.
def replace_section(section, act, link_conversions, exceptions):
    section_text = section.group()
    try:
        citation, remainder = split_citation(section_text)
    except ValueError:
        return section_text
    if DASH_REGEX.sub("-", citation) in exceptions:
        return section_text
    section = DASH_REGEX.sub("-", SECTION_ID_REGEX.match(citation).group())  # extract section
    # only link if section exists within the relevant act
    if act in link_conversions and section in link_conversions[act]:
        paragraphs = extract_paragraphs(section_text)
        conversion = link_conversions[act][section]
        return USCODE_LINK_FORMAT.format(
            conversion["title"],
            DASH_REGEX.sub("-", conversion["usc"]),
            USCODE_SUBSTRUCT_FORMAT.format("_".join(paragraphs)) if paragraphs else "",
            citation,
        ) + remainder
    return section_text


# This middleman re.sub() function is run when an entire statute ref is matched. It performs another substition on individual
# sections within the ref. It is needed to enforce refs starting with "section" but possibly containing more than one section.
# "link_conversions" and "do_not_link" must be passed in via a partial function.
def replace_sections(match, link_conversions, exceptions):
    act = match.group(2)
    act = f"{act.strip()} Act" if act else DEFAULT_ACT  # if no act is specified, default to DEFAULT_ACT
    return SECTION_REGEX.sub(
        partial(replace_section, act=act, link_conversions=link_conversions, exceptions=exceptions.get(act, [])),
        match.group(),
    )


# This pattern matches USC citations such as "42 U.S.C. 1901(a)", "42 U.S.C. 1901(a) or (b)",
# "42 U.S.C. 1901(a) and 1902(b)" and more variations, similar to STATUTE_REF_PATTERN.
# Negative lookahead ensures "42 U.S.C. 1234 and 41 U.S.C. 4567" doesn't register "1234" and "41" as two sections in one ref.
USC_PATTERN = r"u.?\s*s.?\s*c.?"
IGNORE_PATTERN = rf"\d+\s*(?:{USC_PATTERN}|c.?\s*f.?\s*r.?)\s*"
USC_REF_PATTERN = rf"(\d+)\s*{USC_PATTERN}\s*((?:{SECTION_PATTERN}{AND_OR_PATTERN}(?!{IGNORE_PATTERN}))+)"
USC_REF_REGEX = re.compile(USC_REF_PATTERN, re.IGNORECASE)


# Replaces individual USC refs with links, to be run by re.sub().
# "title" must be passed in via a partial function.
def replace_usc_citation(match, title, exceptions):
    citation_text = match.group()
    try:
        citation, remainder = split_citation(citation_text)
    except ValueError:
        return citation_text
    if DASH_REGEX.sub("-", citation) in exceptions:
        return citation_text
    section = SECTION_ID_REGEX.match(citation).group()
    paragraphs = extract_paragraphs(citation)
    return USCODE_LINK_FORMAT.format(
        title,
        DASH_REGEX.sub("-", section),
        USCODE_SUBSTRUCT_FORMAT.format("_".join(paragraphs)) if paragraphs else "",
        citation,
    ) + remainder


# Matches entire USC citations to account for "and", "or" scenarios.
def replace_usc_citations(match, exceptions):
    title = match.group(1)
    section = match.group(2)
    return match.group().replace(
        section,
        SECTION_REGEX.sub(
            partial(replace_usc_citation, title=title, exceptions=exceptions.get(title, [])),
            section,
        )
    )


@register.simple_tag
def link_statutes(paragraph, link_conversions, link_config):
    if link_config["link_statute_refs"]:
        paragraph = STATUTE_REF_REGEX.sub(
            partial(replace_sections, link_conversions=link_conversions, exceptions=link_config["statute_ref_exceptions"]),
            paragraph,
        )
    if link_config["link_usc_refs"]:
        paragraph = USC_REF_REGEX.sub(
            partial(replace_usc_citations, exceptions=link_config["usc_ref_exceptions"]),
            paragraph
        )
    return paragraph
