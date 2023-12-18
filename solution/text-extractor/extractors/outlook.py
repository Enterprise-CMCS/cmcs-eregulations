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

    def extract(self, file_path: str) -> str:
        try:
            msg = extract_msg.openMsg(file_path)
        except Exception as e:
            raise ExtractorException(f"msg file failed to extract: {str(e)}")

        body = msg.body
        for attachment in msg.attachments:
            file_name = attachment.longFilename
            file_type = file_name.lower().split('.')[-1]

            with NamedTemporaryFile(delete=False) as file:
                file.write(attachment.data)
                file.close()

                body += f" {file_name} "

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
