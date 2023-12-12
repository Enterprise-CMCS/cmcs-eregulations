from tempfile import NamedTemporaryFile
import os

import extract_msg

from .exceptions import ExtractorException
from .extractor import Extractor


class OutlookExtractor(Extractor):
    file_types = ("msg",)

    def __init__(self, file_type: str, config: dict):
        super().__init__(file_type, config)
        self.config = config

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

                try:
                    extractor = Extractor.get_extractor(file_type, self.config)
                    text = extractor.extract(file.name)
                    body += f" {file_name} {text}"
                except ExtractorInitException as e:
                    raise ExtractorException(f"failed to initialize extractor for attachment \"{file_name}\": {str(e)}")
                except ExtractorException as e:
                    raise ExtractorException(f"failed to extract text for attachment \"{file_name}\": {str(e)}")
                except Exception as e:
                    raise ExtractorException(f"extracting text for attachment \"{file_name}\" failed unexpectedly: {str(e)}")

        return body
