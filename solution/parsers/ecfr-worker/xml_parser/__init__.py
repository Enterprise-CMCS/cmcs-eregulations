"""XML parsing pipeline for eCFR part documents.

This package converts raw eCFR XML into the normalized eRegs `document`
payload shape used by part uploads.
"""

from .errors import EcfrXmlParseError
from .parse import parse_part_xml_to_document

__all__ = ["EcfrXmlParseError", "parse_part_xml_to_document"]
