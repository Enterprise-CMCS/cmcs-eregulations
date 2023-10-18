from tempfile import TemporaryDirectory
from pathlib import Path

from pdf2image import convert_from_bytes
import boto3

from .extractors import Extractor
from .exceptions import ExtractorInitException


class PdfExtractor(Extractor):
    file_types = ("application/pdf",)

    def __init__(self, file_type: str, config: dict):
        super().__init__(file_type, config)
        try:
            self.aws_access_key_id = config["textract"]["aws_access_key_id"]
            self.aws_secret_access_key = config["textract"]["aws_secret_access_key"]
            self.aws_region = config["textract"]["aws_region"]
        except KeyError:
            raise ExtractorInitException("to handle PDFs, the POST body must include a 'textract' dict with "
                                         "'aws_access_key_id', 'aws_secret_access_key', and 'aws_region' keys.")
        try:
            self.client = boto3.client(
                "textract",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region,
            )
        except Exception as e:
            raise ExtractorInitException(f"failed to initialize AWS client: {str(e)}")

    def _convert_to_images(self, file: bytes, temp_dir: str) -> [str]:
        return convert_from_bytes(
            file,
            paths_only=True,
            output_folder=temp_dir,
            fmt="jpeg",
        )

    def extract(self, file: bytes) -> str:
        text = ""
        with TemporaryDirectory() as temp_dir:
            try:
                pages = _convert_to_images(file, temp_dir)
            except Exception as e:
                raise ExtractorException(f"failed to convert PDF to images: {str(e)}")
            for page in pages:
                try:
                    with open(page, "rb") as f:
                        content = f.read()
                except Exception as e:
                    raise ExtractorException(f"failed to read temporary image file: {str(e)}")
                try:
                    response = client.detect_document_text(Document={'Bytes': bytes})
                except Exception as e:
                    raise ExtractorException(f"AWS Textract client failed: {str(e)}")
                try:
                    for item in response["Blocks"]:
                        if item["BlockType"] == "LINE":
                            text += item["Text"]
                except KeyError:
                    raise ExtractorException(f"AWS response formatted improperly: {str(e)}"
        return text
