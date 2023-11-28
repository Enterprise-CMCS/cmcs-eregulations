from .exceptions import BackendInitException


# Base class for file backends
# Child classes are automatically registered when added to __init__.py
class FileBackend:
    @classmethod
    def get_backend(cls, backend: str, config: dict = {}) -> "FileBackend":
        try:
            return {subclass.backend: subclass for subclass in cls.__subclasses__()}[backend](config)
        except KeyError:
            backends = [subclass.backend for subclass in cls.__subclasses__()]
            supported = "'" + "', '".join(backends) + "'"
            raise BackendInitException(f"'{backend}' is not a valid backend. Supported backends are: {supported}.")

    def __init__(self, config: dict):
        pass

    def get_file(self, temp_directory: str, uri: str) -> str:
        raise NotImplementedError("get_file function not implemented")
