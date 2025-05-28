import re
from functools import partial

from common.patterns import (
    AND_OR_PATTERN,
    DASH_PATTERN,
    DASH_REGEX,
    LINKED_PARAGRAPH_REGEX,
    PARAGRAPH_EXTRACT_REGEX,
    PARAGRAPH_PATTERN,
    USC_CFR_IGNORE_PATTERN,
)
from regulations.models import (
    RegulationLinkConfiguration,
    StatuteLinkConfiguration,
    StatuteLinkConverter,
)

USCODE_ANCHOR_FORMAT = '<a target="_blank" rel="noopener noreferrer" class="external" href="{}">{}</a>'
USCODE_LINK_FORMAT = 'https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title{}-section{}&num=0&edition=prelim{}'
USCODE_SUBSTRUCT_FORMAT = "#substructure-location_{}"

NUMBER_PATTERN = r"[0-9]+"

# Extracts the section ID only, for example "1902-1G" and its variations.
SECTION_ID_PATTERN = rf"\d+[a-z]*(?:(?:{DASH_PATTERN})+[a-z0-9]+)?"

# Matches individual sections, for example "1902(a)(2) and (b)(1)" and its variations.
SECTION_PATTERN = rf"{SECTION_ID_PATTERN}(?:{AND_OR_PATTERN}{PARAGRAPH_PATTERN})*"

# Matches entire statute references, including one or more sections and an optional Act.
# For example, "Sections 1902(a)(2) and (b)(1) and 1903(b) of the Social Security Act" and its variations.
# Will also match "Section 1902" if the section is contained within the DEFAULT_ACT. See tests for more complete examples.
STATUTE_REF_PATTERN = rf"(?:\bsec(?:tions?|t?s?)?|§|&#xA7;)\.?\s*((?:{SECTION_PATTERN}{AND_OR_PATTERN})+)"\
                      r"(?:\s*of\s*the\s*([a-z0-9\s]*?(?=\bact\b)))?"

# Regex's are precompiled to improve page load time.
SECTION_ID_REGEX = re.compile(rf"({SECTION_ID_PATTERN})", re.IGNORECASE)
SECTION_REGEX = re.compile(rf"({SECTION_PATTERN})", re.IGNORECASE)
STATUTE_REF_REGEX = re.compile(STATUTE_REF_PATTERN, re.IGNORECASE)
NUMBER_REGEX = re.compile(NUMBER_PATTERN, re.IGNORECASE)

# The act to use if none is specified, for example "section 1902 of the act" defaults to this.
DEFAULT_ACT = "Social Security Act"


# Create a mixin class that adds link conversions to the serializer context.
class LinkConversionsMixin:
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["link_conversions"] = self.get_link_conversions()
        return context

    def get_link_conversions(self):
        # This method should be overridden to provide the actual link conversions.
        conversions = {}
        for section, usc, act, title in StatuteLinkConverter.objects.values_list("section", "usc", "act", "title"):
            if act not in conversions:
                conversions[act] = {}
            conversions[act][section] = {
                "title": title,
                "usc": usc,
            }
        return conversions

# Create a mixin that adds exceptions to the serializer context.
class LinkConfigMixin:
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["link_config"] = self.get_link_config()
        return context

    def get_link_config(self):
        # This method should be overridden to provide the actual exceptions.

        statute_link_config = StatuteLinkConfiguration.get_solo()
        reg_link_config = RegulationLinkConfiguration.get_solo()
        return {
            "link_statute_refs": statute_link_config.link_statute_refs,
            "link_usc_refs": statute_link_config.link_usc_refs,
            "statute_ref_exceptions": statute_link_config.statute_ref_exceptions_dict,
            "usc_ref_exceptions": statute_link_config.usc_ref_exceptions_dict,
            "link_cfr_refs": reg_link_config.link_cfr_refs,
            "cfr_ref_exceptions": reg_link_config.cfr_ref_exceptions_dict,
        }


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
    return PARAGRAPH_EXTRACT_REGEX.findall(linked_paragraphs.group()) if linked_paragraphs else None


# This function is run by re.sub() to replace individual section refs with links.
# "act" and "link_conversions" must be passed in via a partial function.
def replace_section(section, act, link_conversions, exceptions, generate_url_only=False):
    section_text = section.group()
    try:
        citation, remainder = split_citation(section_text)
    except ValueError:
        return section_text
    if DASH_REGEX.sub("-", citation) in exceptions:
        return "" if generate_url_only else section_text
    section = DASH_REGEX.sub("-", SECTION_ID_REGEX.match(citation).group())  # extract section
    # only link if section exists within the relevant act
    if act in link_conversions and section in link_conversions[act]:
        paragraphs = extract_paragraphs(section_text)
        conversion = link_conversions[act][section]
        link = USCODE_LINK_FORMAT.format(
            conversion["title"],
            DASH_REGEX.sub("-", conversion["usc"]),
            USCODE_SUBSTRUCT_FORMAT.format("_".join(paragraphs)) if paragraphs else "",
            citation,
        )
        if not generate_url_only:
            return USCODE_ANCHOR_FORMAT.format(link, citation) + remainder
        return link
    return "" if generate_url_only else section_text


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
USC_REF_PATTERN = rf"(\d+)\s*u.?\s*s.?\s*c.?\s*((?:{SECTION_PATTERN}{AND_OR_PATTERN}(?!{USC_CFR_IGNORE_PATTERN}))+)"
USC_REF_REGEX = re.compile(USC_REF_PATTERN, re.IGNORECASE)


# Replaces individual USC refs with links, to be run by re.sub().
# "title" must be passed in via a partial function.
def replace_usc_citation(match, title, exceptions, generate_url_only=False):
    citation_text = match.group()
    try:
        citation, remainder = split_citation(citation_text)
    except ValueError:
        return citation_text
    if DASH_REGEX.sub("-", citation) in exceptions:
        return "" if generate_url_only else citation_text
    section = SECTION_ID_REGEX.match(citation).group()
    paragraphs = extract_paragraphs(citation)
    link = USCODE_LINK_FORMAT.format(
        title,
        DASH_REGEX.sub("-", section),
        USCODE_SUBSTRUCT_FORMAT.format("_".join(paragraphs)) if paragraphs else "",
        citation,
    )
    if not generate_url_only:
        return USCODE_ANCHOR_FORMAT.format(link, citation) + remainder
    return link


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
