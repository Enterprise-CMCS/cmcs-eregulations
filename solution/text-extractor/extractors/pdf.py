from tempfile import TemporaryDirectory

import boto3
from pdf2image import convert_from_bytes

from .exceptions import ExtractorException, ExtractorInitException
from .extractor import Extractor


class PdfExtractor(Extractor):
    file_types = ("application/pdf", 'pdf')

    def __init__(self, file_type: str, config: dict):
        super().__init__(file_type, config)
        try:
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
        return convert_from_bytes(
            file,
            paths_only=True,
            output_folder=temp_dir,
            fmt="jpeg",
        )

    def extract(self, file_path: str) -> str:
        text = ""
        with TemporaryDirectory() as temp_dir:
            try:
                with open(file_path, 'rb') as pdf_file:
                    pdf = pdf_file.read()
                    pages = self._convert_to_images(pdf, temp_dir)

            except Exception as e:
                raise ExtractorException(f"failed to convert PDF to images: {str(e)}")
            for page in pages:
                try:
                    with open(page, "rb") as f:
                        content = f.read()
                except Exception as e:
                    raise ExtractorException(f"failed to read temporary image file: {str(e)}")
                try:
                    response = self.client.detect_document_text(Document={'Bytes': content})
                except Exception as e:
                    raise ExtractorException(f"AWS Textract client failed: {str(e)}")
                try:
                    for item in response["Blocks"]:
                        if item["BlockType"] == "LINE":
                            text += item["Text"] + " "
                except KeyError as e:
                    raise ExtractorException(f"AWS response formatted improperly: {str(e)}")
        return text
