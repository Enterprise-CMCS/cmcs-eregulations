import logging
import os
from tempfile import TemporaryDirectory

import docx2txt

from .exceptions import (
    ExtractorException,
    ExtractorInitException,
)
from .extractor import Extractor

logger = logging.getLogger(__name__)


class WordExtractor(Extractor):
    file_types = ("docx",)

    def extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        with TemporaryDirectory() as temp_dir:
            text = docx2txt.process(file_path, temp_dir)
            for file in os.listdir(temp_dir):
                full_path = os.path.join(temp_dir, file)
                # Run extractor for embedded files
                with open(full_path, "rb") as f:
                    data = f.read()
                file_type = file.lower().split('.')[-1]
                try:
                    extractor = Extractor.get_extractor(file_type, self.config)
                    text += f" {extractor.extract(data)}"
                except ExtractorInitException as e:
                    logger.log(logging.WARN, "Failed to initialize extractor for embedded file \"%s\": %s", file, str(e))
                except ExtractorException as e:
                    logger.log(logging.WARN, "Failed to extract text for embedded file \"%s\": %s", file, str(e))
                except Exception as e:
                    logger.log(logging.WARN, "Extracting text for embedded file \"%s\" failed unexpectedly: %s", file, str(e))
        return text
