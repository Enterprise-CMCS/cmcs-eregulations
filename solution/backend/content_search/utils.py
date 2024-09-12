import unicodedata


# Remove control characters from a string
#
# text: str - the text to remove control characters from
# returns: str - the text with control characters removed
def remove_control_characters(text: str) -> str:
    return "".join(ch if not unicodedata.category(ch).lower().startswith("c") else " " for ch in text).strip()
