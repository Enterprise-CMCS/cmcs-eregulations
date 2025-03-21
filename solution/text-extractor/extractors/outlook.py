import os
import logging

import extract_msg

from .exceptions import (
    ExtractorException,
)
from .extractor import Extractor

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class OutlookExtractor(Extractor):
    file_types = ("outlook",)

    def _handle_data(self, attachment: extract_msg.Attachment) -> str:
        file_name = attachment.longFilename
        if not file_name:
            logger.warning("A data attachment failed to extract because it has no filename.")
            return ""
        return f" {file_name} {self._extract_embedded(file_name, attachment.data)}"

    def _handle_message(self, message: extract_msg.Message) -> str:
        logger.debug("Handling embedded message object.")
        body = message.body if message.body else ""  # Handles cases where an embedded message's body is empty
        for attachment in message.attachments:
            if attachment.type == extract_msg.enums.AttachmentType.DATA:
                logger.debug("Attachment is data, extracting.")
                body += self._handle_data(attachment)
            elif attachment.type == extract_msg.enums.AttachmentType.MSG:
                logger.debug("Attachment is another message object, extracting.")
                body += self._handle_message(attachment.data)
        return body

    def _extract(self, file: bytes) -> str:
        try:
            msg = extract_msg.openMsg(file)
        except Exception as e:
            raise ExtractorException(f"msg file failed to extract: {str(e)}")

        return self._handle_message(msg)
