import os
import email
import logging

from .exceptions import (
    ExtractorException,
)
from .extractor import Extractor

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class EmailExtractor(Extractor):
    file_types = ("eml",)

    def _extract_payload(self, message):
        payload = message.get_payload()

        if isinstance(payload, list):
            logger.debug("Encountered embedded payload group, extracting.")
            text = ""
            for i in payload:
                text += f" {self._extract_payload(i)}"
            return text

        if not message.get_filename() and message.get_content_type() == "text/plain":
            logger.debug("Encountered message plain text, extracting.")
            return f" {payload}"

        if not message.get_filename():
            logger.debug("Encountered unsupported payload, skipping.")
            return ""

        file_name = message.get_filename()
        logger.debug("Assuming payload \"%s\" is embedded file, extracting.", file_name)
        text = self._extract_embedded(
            file_name,
            message.get_payload(decode=True),
        )
        return f" {file_name} {text}"

    def _extract(self, file: bytes) -> str:
        try:
            msg = email.message_from_bytes(file)
        except Exception as e:
            raise ExtractorException(f"eml file failed to extract: {str(e)}")

        return self._extract_payload(msg)
