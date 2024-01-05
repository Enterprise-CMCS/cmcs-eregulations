import logging
from tempfile import NamedTemporaryFile

from pptx import Presentation

from .exceptions import (
    ExtractorException,
    ExtractorInitException,
)
from .extractor import Extractor

logger = logging.getLogger(__name__)


class PowerPointExtractor(Extractor):
    file_types = ("pptx",)

    def extract(self, file_path: str) -> str:
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
                        with NamedTemporaryFile(delete=False) as file:
                            file.write(image.blob)
                            file.close()

                            # Run extractor for embedded file
                            try:
                                extractor = Extractor.get_extractor(file_type, self.config)
                                text += f" {extractor.extract(file.name)}"
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
