from .extractor import Extractor


class TextExtractor(Extractor):
    file_types = ("text/plain",)

    def extract(self, file: bytes) -> str:
        return file.decode()
