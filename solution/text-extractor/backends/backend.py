from .exceptions import BackendInitException


# Base class for file backends
# Child classes are automatically registered when added to __init__.py
class FileBackend:
    @classmethod
    def get_backend(cls, backend: str, get_params: dict, post_params: dict) -> "FileBackend":
        try:
            return {subclass.backend: subclass for subclass in cls.__subclasses__()}[backend](get_params, post_params)
        except KeyError:
            backends = [subclass.backend for subclass in cls.__subclasses__()]
            supported = "'" + "', '".join(backends) + "'"
            raise BackendInitException(f"'{backend}' is not a valid backend. Supported backends are: {supported}.")

    def __init__(self, get_params: dict, post_params: dict):
        pass

    def get_file(self, uri: str) -> bytes:
        raise NotImplementedError("get_file function not implemented")
