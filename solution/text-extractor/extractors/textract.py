import logging

import boto3

from .exceptions import ExtractorException, ExtractorInitException
from .extractor import Extractor

logger = logging.getLogger(__name__)


class TextractExtractor(Extractor):
    file_types = ("tiff", "jpeg", "png")

    def __init__(self, file_type: str, config: dict):
        super().__init__(file_type, config)
        try:
            logger.debug("Initializing boto3 client.")
            self.client = boto3.client(
                "textract",
                **self._get_aws_arguments(config),
            )
        except Exception as e:
            raise ExtractorInitException(f"failed to initialize Textract client: {str(e)}")

    def _get_aws_arguments(self, config: dict) -> dict:
        logger.debug("Retrieving AWS parameters from config...")
        try:
            return {
                "aws_access_key_id": config["aws"]["aws_access_key_id"],
                "aws_secret_access_key": config["aws"]["aws_secret_access_key"],
                "region_name": config["aws"]["aws_region"],
            }
            logger.debug("Retrieved AWS parameters from config.")
        except KeyError:
            logger.warning("Failed to retrieve AWS parameters from config, using default parameters.")
            return {
                "config": boto3.session.Config(signature_version='s3v4'),
            }

    def _extract(self, file: bytes) -> str:
        try:
            logger.debug("Sending image bytes to AWS Textract.")
            response = self.client.detect_document_text(Document={'Bytes': file})
        except Exception as e:
            raise ExtractorException(f"AWS Textract client failed: {str(e)}")
        try:
            logger.debug("Parsing AWS Textract response.")
            text = ""
            for item in response["Blocks"]:
                if item["BlockType"] == "LINE":
                    text += item["Text"] + " "
            return text
        except KeyError as e:
            raise ExtractorException(f"AWS Textract response formatted improperly: {str(e)}")
        except Exception as e:
            raise ExtractorException(f"unexpected failure while parsing AWS Textract response: {str(e)}")
