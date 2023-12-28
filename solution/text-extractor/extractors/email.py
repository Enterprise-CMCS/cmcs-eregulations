import email
import logging

from .exceptions import (
    ExtractorException,
)
from .extractor import Extractor

logger = logging.getLogger(__name__)


class EmailExtractor(Extractor):
    file_types = ("eml",)

    def _extract_payload(self, message):
        payload = message.get_payload()

        if isinstance(payload, list):
            text = ""
            for i in payload:
                text += f" {self._extract_payload(i)}"
            return text

        if not message.get_filename() and message.get_content_type() == "text/plain":
            return f" {payload}"

        if not message.get_filename():
            return ""

        file_name = message.get_filename()
        text = self._extract_embedded(
            message.get_filename(),
            message.get_payload(decode=True),
        )
        return f" {file_name} {text}"

    def extract(self, file: bytes) -> str:
        try:
            msg = email.message_from_bytes(file)
        except Exception as e:
            raise ExtractorException(f"eml file failed to extract: {str(e)}")

        return self._extract_payload(msg)
