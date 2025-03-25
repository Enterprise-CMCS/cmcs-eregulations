import os
import io
import logging

from PIL import Image

from .extractor import Extractor

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class ImageExtractor(Extractor):
    file_types = ("gif", "bmp", "tga", "webp",)

    def __init__(self, file_type: str, config: dict):
        super().__init__(file_type, config)
        self.extractor = Extractor.get_extractor("jpeg", config)

    def _extract(self, file: bytes) -> str:
        image = Image.open(io.BytesIO(file))
        if not image.mode == "RGB":
            image = image.convert("RGB")
        output = io.BytesIO()
        image.save(output, format="jpeg", quality=95)
        return self.extractor.extract(output.getvalue())
