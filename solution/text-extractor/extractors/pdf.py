import logging
from tempfile import TemporaryDirectory

import boto3
from pdf2image import convert_from_bytes

from .exceptions import ExtractorException, ExtractorInitException
from .extractor import Extractor

logger = logging.getLogger(__name__)


class PdfExtractor(Extractor):
    file_types = ("application/pdf", 'pdf')

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
        try:
            return {
                "aws_access_key_id": config["aws"]["aws_access_key_id"],
                "aws_secret_access_key": config["aws"]["aws_secret_access_key"],
                "region_name": config["aws"]["aws_region"],
            }
        except KeyError:
            return {
                "config": boto3.session.Config(signature_version='s3v4',),
            }

    def _convert_to_images(self, file: bytes, temp_dir: str) -> [str]:
        logger.debug("Converting PDF file to images stored in a temporary directory.")
        return convert_from_bytes(
            file,
            paths_only=True,
            output_folder=temp_dir,
            fmt="jpeg",
        )

    def extract(self, file: bytes) -> str:
        with TemporaryDirectory() as temp_dir:
            try:
                pages = self._convert_to_images(file, temp_dir)
            except Exception as e:
                raise ExtractorException(f"failed to convert PDF to images: {str(e)}")

            text = ""
            for i, page in enumerate(pages):
                logger.debug("Extracting page %i.", i)
                try:
                    with open(page, "rb") as f:
                        content = f.read()
                except Exception as e:
                    raise ExtractorException(f"failed to read temporary image file: {str(e)}")
                try:
                    logger.debug("Sending page bytes to AWS Textract.")
                    response = self.client.detect_document_text(Document={'Bytes': content})
                except Exception as e:
                    raise ExtractorException(f"AWS Textract client failed: {str(e)}")
                try:
                    logger.debug("Parsing AWS Textract response.")
                    for item in response["Blocks"]:
                        if item["BlockType"] == "LINE":
                            text += item["Text"] + " "
                except KeyError as e:
                    raise ExtractorException(f"AWS response formatted improperly: {str(e)}")

        return text
