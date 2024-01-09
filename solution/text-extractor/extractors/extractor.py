import logging
from tempfile import NamedTemporaryFile

from .exceptions import (
    ExtractorException,
    ExtractorInitException,
)

logger = logging.getLogger(__name__)


# Base class for text extraction
# Child classes are automatically registered when added to __init__.py
class Extractor:
    @classmethod
    def get_extractor(cls, file_type: str, config: dict = {}) -> "Extractor":
        logger.info("Attempting to initialize extractor for file type \"%s\".", file_type)
        type_map = {f: subclass for subclass in cls.__subclasses__() for f in subclass.file_types}
        try:
            extractor_class = type_map[file_type]
            logger.info("Found matching extractor class \"%s\".", str(extractor_class))
            extractor = extractor_class(file_type, config)
            logger.info("Extractor initialized successfully.")
            return extractor
        except KeyError:
            raise ExtractorInitException(f"'{file_type}' is an unsupported file type.")

    def __init__(self, file_type: str, config: dict):
        self.file_type = file_type
        self.config = config

    def _write_file(self, data: bytes) -> str:
        file = NamedTemporaryFile(delete=False, suffix=f".{self.file_type}")
        file.write(data)
        file.close()
        logger.debug("Wrote file contents to temporary file \"%s\".", file.name)
        return file.name

    def _extract_embedded(self, file_name: str, file: bytes) -> str:
        logger.info("Extracting embedded file \"%s\".", file_name)
        try:
            file_type = file_name.lower().split(".")[-1]
            extractor = Extractor.get_extractor(file_type, self.config)
            return extractor.extract(file)
        except ExtractorInitException as e:
            logger.warning("Failed to initialize extractor for embedded file \"%s\": %s", file_name, str(e))
        except ExtractorException as e:
            logger.warning("Failed to extract text for embedded file \"%s\": %s", file_name, str(e))
        except Exception as e:
            logger.warning("Extracting text for embedded file \"%s\" failed unexpectedly: %s", file_name, str(e))
        return ""

    def extract(self, file: bytes) -> str:
        raise NotImplementedError(f"extract function not implemented for '{self.file_type}'")
