import logging
from tempfile import TemporaryDirectory

from pdf2image import convert_from_bytes

from .exceptions import ExtractorException
from .extractor import Extractor

logger = logging.getLogger(__name__)


class PdfExtractor(Extractor):
    file_types = ("pdf",)
    max_size = 20

    def __init__(self, file_type: str, config: dict):
        super().__init__(file_type, config)
        self.extractor = Extractor.get_extractor("jpeg", config)

    def _convert_to_images(self, file: bytes, temp_dir: str) -> [str]:
        logger.debug("Converting PDF file to images stored in a temporary directory.")
        return convert_from_bytes(
            file,
            paths_only=True,
            output_folder=temp_dir,
            fmt="jpeg",
        )

    def _extract(self, file: bytes) -> str:
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
                    text += " " + self.extractor.extract(content)
                except ExtractorException as e:
                    logger.warning("Page %i failed to extract: %s", i, str(e))
                except Exception as e:
                    logger.warning("Page %i unexpectedly failed to extract: %s", i, str(e))
        return text
