import logging

import extract_msg

from .exceptions import (
    ExtractorException,
)
from .extractor import Extractor

logger = logging.getLogger(__name__)


class OutlookExtractor(Extractor):
    file_types = ("msg",)

    def _handle_data(self, attachment: extract_msg.attachment.Attachment) -> str:
        file_name = attachment.longFilename
        if not file_name:
            logger.log(logging.WARN, "A data attachment failed to extract because it has no filename.")
            return ""
        return f" {file_name} {self._extract_embedded(file_name, attachment.data)}"

    def _handle_message(self, message: extract_msg.message.Message) -> str:
        body = message.body
        for attachment in message.attachments:
            if attachment.type == "data":
                body += self._handle_data(attachment)
            elif attachment.type == "msg":
                body += self._handle_message(attachment.data)
        return body

    def extract(self, file: bytes) -> str:
        try:
            msg = extract_msg.openMsg(file)
        except Exception as e:
            raise ExtractorException(f"msg file failed to extract: {str(e)}")

        return self._handle_message(msg)
