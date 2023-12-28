import logging
import os
import zipfile
from tempfile import TemporaryDirectory

from .exceptions import (
    ExtractorException,
    ExtractorInitException,
)
from .extractor import Extractor

logger = logging.getLogger(__name__)


class ZipExtractor(Extractor):
    file_types = ("zip",)

    def extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        full_text = ""

        with TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                zip_file.extractall(temp_dir)

            for root, directories, files in os.walk(temp_dir):
                for file_name in files:
                    file_type = file_name.lower().split('.')[-1]
                    file_path = os.path.abspath(os.path.join(root, file_name))

                    with open(file_path, "rb") as f:
                        data = f.read()

                    try:
                        extractor = Extractor.get_extractor(file_type, self.config)
                        text = extractor.extract(data)
                        full_text += f" {file_name} {text}"
                    except ExtractorInitException as e:
                        logger.log(logging.WARN, "Failed to initialize extractor for zipped file \"%s\": %s", file_name, str(e))
                    except ExtractorException as e:
                        logger.log(logging.WARN, "Failed to extract text for zipped file \"%s\": %s", file_name, str(e))
                    except Exception as e:
                        logger.log(
                            logging.WARN,
                            "Extracting text for zipped file \"%s\" failed unexpectedly: %s",
                            file_name,
                            str(e),
                        )

        return full_text
