# Functions and mixins that are exportable to other apps may go here

from django.core.exceptions import BadRequest
from django.db.models import Q


# Returns True if x is an integer, False otherwise.
def is_int(x):
    try:
        _ = int(x)
        return True
    except ValueError:
        return False


# Generates an OR'd together Q query of all citations passed in via the "citations" argument.
# The results of this function may be passed directly into a Django 'filter' call or manipulated like any Q object.
#
# For example, pass in ["42.433.1", "42.433.2"] and get:
#     (Q(title=42) & Q(part=433) & Q(section_id=1)) | (Q(title=42) & Q(part=433) & Q(section_id=2))
#
# citations: list of citation strings
# filter_prefix: query prefix for nested citations (e.g. "cfr_citations__" or "resources__cfr_citations__")
# max_depth: restrict searching to titles (=1) or parts (=2)
def get_citation_filter(citations, filter_prefix, max_depth=100):
    queries = []
    for loc in citations:
        split = loc.split(".")
        length = len(split)

        if length < 1 or \
                (length >= 1 and not is_int(split[0])) or \
                (length >= 2 and (not is_int(split[0]) or not is_int(split[1]))):
            raise BadRequest(f"\"{loc}\" is not a valid title, part, section, or subpart!")

        q = Q(**{f"{filter_prefix}title": split[0]})
        if length > 1:
            if max_depth < 2:
                raise BadRequest(f"\"{loc}\" is too specific. You may only specify titles.")
            q &= Q(**{f"{filter_prefix}part": split[1]})
            if length > 2:
                if max_depth < 3:
                    raise BadRequest(f"\"{loc}\" is too specific. You may only specify titles and parts.")
                q &= (
                    Q(**{f"{filter_prefix}section__section_id": split[2]})
                    if is_int(split[2])
                    else (
                            Q(**{f"{filter_prefix}subpart__subpart_id": split[2]}) |
                            Q(**{f"{filter_prefix}section__parent__subpart_id": split[2]})
                    )
                )

        queries.append(q)

    q_obj = Q()
    for q in queries:
        q_obj |= q
    return q_obj


# Convert a boolean value encoded as a string to a bool.
#
# 'true', 't', 'y', 'yes', '1' all return True.
# 'false', 'f', 'n', 'no', '0' all return False.
#
# value: the string to convert to a bool (case insensitive)
# default: the default to return if 'value' is None
def string_to_bool(value, default):
    if not value:
        return default
    value = value.lower().strip()
    if value in ("true", "t", "y", "yes", "1"):
        return True
    elif value in ("false", "f", "n", "no", "0"):
        return False
    raise ValueError(f"The value '{value}' cannot be converted to a bool.")
