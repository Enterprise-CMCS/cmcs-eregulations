from .exceptions import (
    BackendInitException,
)


class FileBackend:
    @classmethod
    def get_backend(cls, backend, get_params, post_params):
        try:
            return {subclass.backend: subclass for subclass in cls.__subclasses__()}[backend](get_params, post_params)
        except KeyError:
            backends = [subclass.backend for subclass in cls.__subclasses__()]
            supported = "'" + "', '".join(backends) + "'"
            raise BackendInitException(f"'{backend}' is not a valid backend. Supported backends are: {supported}.")

    def __init__(self, get_params, post_params):
        pass

    def get_file(self):
        raise NotImplementedError


