import logging

from pptx import Presentation

from .exceptions import (
    ExtractorException,
    ExtractorInitException,
)
from .extractor import Extractor

logger = logging.getLogger(__name__)


class PowerPointExtractor(Extractor):
    file_types = ("pptx",)

    def extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        text = ""
        presentation = Presentation(file_path)

        for slide in presentation.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += f" {shape.text}"
                if hasattr(shape, "image"):
                    image = shape.image
                    if hasattr(image, "ext"):
                        file_type = image.ext

                        # Run extractor for embedded file
                        try:
                            extractor = Extractor.get_extractor(file_type, self.config)
                            text += f" {extractor.extract(image.blob)}"
                        except ExtractorInitException as e:
                            logger.log(
                                logging.WARN,
                                "Failed to initialize extractor for embedded %s file: %s",
                                file_type,
                                str(e),
                            )
                        except ExtractorException as e:
                            logger.log(
                                logging.WARN,
                                "Failed to extract text for embedded %s file: %s",
                                file_type,
                                str(e),
                            )
                        except Exception as e:
                            logger.log(
                                logging.WARN,
                                "Extracting text for embedded %s file failed unexpectedly: %s",
                                file_type,
                                str(e),
                            )

        return text
