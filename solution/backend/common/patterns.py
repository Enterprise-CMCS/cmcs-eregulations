# This file contains regex patterns used in more than one location throughout eRegs.

import re

# For negative lookahead to ensure "42 U.S.C. 1234 and 41 CFR 7890" doesn't register "1234" and "41" as two sections in one ref.
USC_CFR_IGNORE_PATTERN = r"\d+\s*(?:u.?\s*s.?\s*c.?|c.?\s*f.?\s*r.?)\s*"

# Matches ", and", ", or", "and", "or", "&", and more variations.
CONJUNCTION_PATTERN = r"(?:,?\s*(?:and|or|through|\&)?\s*)?"

# Matches all forms of dashes.
DASH_PATTERN = r"[-—–-–]|&#x2013;"
DASH_REGEX = re.compile(DASH_PATTERN, re.IGNORECASE)

PARAGRAPH_PATTERN = r"\([a-z0-9]+\)"

# Matches chains of paragraphs, for example in "Section 1902(a)(1)(C)", "(a)(1)(C)" will match.
LINKED_PARAGRAPH_PATTERN = rf"((?:{PARAGRAPH_PATTERN})+)"
LINKED_PARAGRAPH_REGEX = re.compile(LINKED_PARAGRAPH_PATTERN, re.IGNORECASE)

# Extracts paragraph identifiers. Running findall() on "(a)(1)(C)" returns ["a", "1", "C"].
PARAGRAPH_EXTRACT_PATTERN = r"\(([a-z0-9]+)\)"
PARAGRAPH_EXTRACT_REGEX = re.compile(PARAGRAPH_EXTRACT_PATTERN, re.IGNORECASE)

# Matches "section", "sections", "sect", "sects", "§", "§.", and variations.
SECTION_LABEL_PATTERN = r"(?:\bsec(?:tions?|t?s?)?|§|&#xA7;)\.?\s*"

# Extracts the section ID only, for example "1902-1G" and its variations.
SECTION_ID_PATTERN = rf"\d+[a-z]*(?:(?:{DASH_PATTERN})+[a-z0-9]+)?"
SECTION_ID_REGEX = re.compile(rf"({SECTION_ID_PATTERN})", re.IGNORECASE)
