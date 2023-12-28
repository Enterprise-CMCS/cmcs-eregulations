from tempfile import NamedTemporaryFile

from .exceptions import ExtractorInitException


# Base class for text extraction
# Child classes are automatically registered when added to __init__.py
class Extractor:
    @classmethod
    def get_extractor(cls, file_type: str, config: dict = {}) -> "Extractor":
        type_map = {f: subclass for subclass in cls.__subclasses__() for f in subclass.file_types}
        try:
            return type_map[file_type](file_type, config)
        except KeyError:
            raise ExtractorInitException(f"'{file_type}' is an unsupported file type.")

    def __init__(self, file_type: str, config: dict):
        self.file_type = file_type
        self.config = config

    def _write_file(self, data: bytes) -> str:
        file = NamedTemporaryFile(delete=False)
        file.write(data)
        file.close()
        return file.name

    def extract(self, file: bytes) -> str:
        raise NotImplementedError(f"extract function not implemented for '{self.file_type}'")
