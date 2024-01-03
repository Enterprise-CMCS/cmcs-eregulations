from striprtf.striprtf import rtf_to_text

from .extractor import Extractor


class RichTextExtractor(Extractor):
    file_types = ("rtf",)

    def extract(self, file_path: str) -> str:
        with open(file_path, "r") as f:
            data = f.read()
        return rtf_to_text(data, errors="replace")
