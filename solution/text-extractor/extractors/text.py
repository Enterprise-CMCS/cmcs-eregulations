from bs4 import UnicodeDammit

from .extractor import Extractor


class TextExtractor(Extractor):
    file_types = ("txt",)

    def extract(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            data = f.read()
        extractor = UnicodeDammit(data)
        return extractor.unicode_markup
