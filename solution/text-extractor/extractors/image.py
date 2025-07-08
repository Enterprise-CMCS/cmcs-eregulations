import os
import io
import logging

from PIL import Image

from .exceptions import ExtractorException, ExtractorInitException
from .extractor import Extractor

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class ImageExtractor(Extractor):
    _convert_to_jpeg = ("gif", "bmp", "tga", "webp")
    file_types = (*_convert_to_jpeg, "tiff", "jpeg", "png")

    def __init__(self, file_type: str, config: dict):
        super().__init__(file_type, config)
        try:
            self.client = self._get_boto3_client("textract")
        except Exception as e:
            raise ExtractorInitException(f"failed to initialize Textract client: {str(e)}")

    def _extract(self, file: bytes) -> str:
        # Check if the file type is in the list of types that need conversion to JPEG
        if self.file_type in self._convert_to_jpeg:
            try:
                # Attempt to convert the image to JPEG
                logger.debug("Converting image to JPEG format.")
                image = Image.open(io.BytesIO(file))
                if not image.mode == "RGB":
                    image = image.convert("RGB")
                output = io.BytesIO()
                image.save(output, format="jpeg", quality=95)
                image.close()
                file = output.getvalue()
                output.close()
            except Exception as e:
                raise ExtractorException(f"failed to convert image to JPEG format: {str(e)}")

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
