from .exceptions import (
    ExtractorInitException,
)


class Extractor:
    @classmethod
    def get_extractor(cls, file_type):
        type_map = {f: subclass for subclass in cls.__subclasses__() for f in subclass.file_types}
        try:
            return type_map[file_type]()
        except KeyError:
            raise ExtractorInitException(f"'{file_type}' is an unsupported file type.")

    def extract(self, file):
        raise NotImplementedError


