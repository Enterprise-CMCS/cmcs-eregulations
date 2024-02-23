import io
import logging

from PIL import Image

from .extractor import Extractor

logger = logging.getLogger(__name__)


class ImageExtractor(Extractor):
    file_types = (
        "image/gif",
        "image/jp2",
        "image/jpx",
        "image/bmp",
        "image/x-ms-bmp",
        "image/x-tga",
        "image/webp",
        "application/octet-stream",
    )

    def __init__(self, file_type: str, config: dict):
        super().__init__(file_type, config)
        self.extractor = Extractor.get_extractor("image/jpeg", config)

    def extract(self, file: bytes) -> str:
        image = Image.open(io.BytesIO(file))
        if not image.mode == "RGB":
            image = image.convert("RGB")
        output = io.BytesIO()
        image.save(output, format="jpeg", quality=95)
        return self.extractor.extract(output.getvalue())
