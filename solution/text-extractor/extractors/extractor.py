import os
import logging
from tempfile import NamedTemporaryFile
import sys

from .exceptions import (
    ExtractorException,
    ExtractorInitException,
)

import boto3
from botocore.client import BaseClient
from magika import Magika, PredictionMode

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

magika = Magika(prediction_mode=PredictionMode.MEDIUM_CONFIDENCE)


# Base class for text extraction
# Child classes are automatically registered when added to __init__.py
class Extractor:
    max_size = -1  # Set this to a value in megabytes to limit the maximum size of the file to extract text from

    @classmethod
    def get_file_type(cls, file: bytes) -> str:
        # Determine the file's content type using Google's Magika ML algorithm
        return magika.identify_bytes(file).output.ct_label

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

    def _get_boto3_client(self, client_type: str) -> type[BaseClient]:
        logger.debug("Initializing boto3 %s client.", client_type)

        try:
            params = {
                "aws_access_key_id": self.config["aws"]["aws_access_key_id"],
                "aws_secret_access_key": self.config["aws"]["aws_secret_access_key"],
                "region_name": self.config["aws"]["aws_region"],
            }
            logger.debug("Retrieved AWS parameters from config.")
        except KeyError:
            logger.warning("Failed to retrieve AWS parameters from config, using default parameters.")
            params = {
                "config": boto3.session.Config(signature_version='s3v4'),
            }

        return boto3.client(
            client_type,
            **params,
        )

    def _write_file(self, data: bytes, **kwargs) -> str:
        extension = kwargs.get("extension")
        extension = f".{extension}" if extension else ""
        file = NamedTemporaryFile(delete=False, suffix=extension)
        file.write(data)
        file.close()
        logger.debug("Wrote file contents to temporary file \"%s\".", file.name)
        return file.name

    def _extract_embedded(self, file_name: str, file: bytes) -> str:
        logger.info("Extracting embedded file \"%s\".", file_name)
        try:
            file_type = Extractor.get_file_type(file)
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
        file_size = sys.getsizeof(file) / 1024 / 1024  # Convert file size to megabytes
        if self.max_size >= 0 and file_size > self.max_size and not self.config.get("ignore_max_size", False):
            raise ExtractorException(f"file size is too large: {int(file_size)}MB > {self.max_size}MB. "
                                     "You may override this with 'ignore_max_size = True'.")
        return self._extract(file)

    def _extract(self, file: bytes) -> str:
        raise NotImplementedError(f"extract function not implemented for '{self.file_type}'")
