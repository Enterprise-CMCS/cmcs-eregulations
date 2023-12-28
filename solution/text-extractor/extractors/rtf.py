from striprtf.striprtf import rtf_to_text

from .extractor import Extractor


class RichTextExtractor(Extractor):
    file_types = ("rtf",)

    def extract(self, file: bytes) -> str:
        return rtf_to_text(file.decode(), errors="replace")
