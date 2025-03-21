import logging
import os
from tempfile import TemporaryDirectory

import docx2txt

from .extractor import Extractor

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class WordExtractor(Extractor):
    file_types = ("docx",)

    def _extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        with TemporaryDirectory() as temp_dir:
            logger.debug("Extracting text. Embedded images stored in temporary directory.")
            text = docx2txt.process(file_path, temp_dir)
            for file in os.listdir(temp_dir):
                logger.debug("Extracting data from embedded image \"%s\".", file)
                full_path = os.path.join(temp_dir, file)
                # Run extractor for embedded files
                with open(full_path, "rb") as f:
                    data = f.read()
                text += f" {self._extract_embedded(file, data)}"
        return text
