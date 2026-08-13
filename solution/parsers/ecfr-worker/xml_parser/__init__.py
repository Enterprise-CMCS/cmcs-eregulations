"""XML parsing pipeline for eCFR part documents.

This package is intentionally skeletal. It defines the integration seam where
raw eCFR XML is converted into the eRegs `document` payload shape.
"""

from .errors import EcfrXmlParseError
from .parse import parse_part_xml_to_document

__all__ = ["EcfrXmlParseError", "parse_part_xml_to_document"]
