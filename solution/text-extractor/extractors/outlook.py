import logging
from tempfile import NamedTemporaryFile

import extract_msg

from .exceptions import (
    ExtractorException,
    ExtractorInitException,
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
        file_type = file_name.lower().split('.')[-1]

        with NamedTemporaryFile(delete=False) as file:
            file.write(attachment.data)
            file.close()

            body = f" {file_name} "

            try:
                extractor = Extractor.get_extractor(file_type, self.config)
                body += extractor.extract(file.name)
            except ExtractorInitException as e:
                logger.log(logging.ERROR, "Failed to initialize extractor for attachment \"%s\": %s", file_name, str(e))
            except ExtractorException as e:
                logger.log(logging.ERROR, "Failed to extract text for attachment \"%s\": %s", file_name, str(e))
            except Exception as e:
                logger.log(logging.ERROR, "Extracting text for attachment \"%s\" failed unexpectedly: %s", file_name, str(e))

            return body

    def _handle_message(self, message: extract_msg.message.Message) -> str:
        body = message.body
        for attachment in message.attachments:
            if attachment.type == "data":
                body += self._handle_data(attachment)
            elif attachment.type == "msg":
                body += self._handle_message(attachment.data)
        return body

    def extract(self, file_path: str) -> str:
        try:
            msg = extract_msg.openMsg(file_path)
        except Exception as e:
            raise ExtractorException(f"msg file failed to extract: {str(e)}")

        return self._handle_message(msg)
