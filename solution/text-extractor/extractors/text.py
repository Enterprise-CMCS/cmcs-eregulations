import textract

from .extractor import Extractor


class TextExtractor(Extractor):
    file_types = ("text/plain",)

    def extract(self, file_path: str) -> str:
        return textract.process(file_path).decode()
