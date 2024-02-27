from bs4 import UnicodeDammit

from .extractor import Extractor


class TextExtractor(Extractor):
    file_types = ("text/plain",)

    def _extract(self, file: bytes) -> str:
        extractor = UnicodeDammit(file)
        return extractor.unicode_markup
