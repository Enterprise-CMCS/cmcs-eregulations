from .exceptions import ExtractorInitException


# Base class for text extraction
# Child classes are automatically registered when added to __init__.py
class Extractor:
    @classmethod
    def get_extractor(cls, file_type: str) -> "Extractor":
        type_map = {f: subclass for subclass in cls.__subclasses__() for f in subclass.file_types}
        try:
            return type_map[file_type](file_type)
        except KeyError:
            raise ExtractorInitException(f"'{file_type}' is an unsupported file type.")

    def __init__(self, file_type: str):
        self.file_type = file_type

    def extract(self, file: bytes) -> str:
        raise NotImplementedError(f"extract function not implemented for '{self.file_type}'")
