import logging
from tempfile import TemporaryDirectory

from pdf2image import convert_from_bytes

from .exceptions import ExtractorException
from .extractor import Extractor

logger = logging.getLogger(__name__)


class PdfExtractor(Extractor):
    file_types = ("pdf",)
    max_pages = 50
    output_file_type = "jpeg"

    def __init__(self, file_type: str, config: dict, *args, **kwargs):
        super().__init__(file_type, config)
        self.output_file_type = kwargs.pop("output_file_type", self.output_file_type)
        self.extractor = Extractor.get_extractor(self.output_file_type, config)

    def _convert_to_images(self, file: bytes, temp_dir: str) -> [str]:
        logger.debug("Converting PDF file to images stored in a temporary directory.")
        return convert_from_bytes(
            file,
            paths_only=True,
            output_folder=temp_dir,
            fmt=self.output_file_type,
        )

    def _extract(self, file: bytes) -> str:
        text = ""

        with TemporaryDirectory() as temp_dir:
            try:
                pages = self._convert_to_images(file, temp_dir)
            except Exception as e:
                raise ExtractorException(f"failed to convert PDF to images: {str(e)}")

            for i, page in enumerate(pages):
                if i >= self.max_pages:
                    logger.warning("Reached maximum number of pages to extract: %i", self.max_pages)
                    break

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
