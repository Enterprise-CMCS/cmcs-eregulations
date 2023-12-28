import logging

from pptx import Presentation

from .extractor import Extractor

logger = logging.getLogger(__name__)


class PowerPointExtractor(Extractor):
    file_types = ("pptx",)

    def extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        presentation = Presentation(file_path)
        text = ""

        for slide in presentation.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += f" {shape.text}"
                if hasattr(shape, "image"):
                    image = shape.image
                    if hasattr(image, "ext"):
                        file_name = f"image.{image.ext}"
                        text += f" {self._extract_embedded(file_name, image.blob)}"
        return text
