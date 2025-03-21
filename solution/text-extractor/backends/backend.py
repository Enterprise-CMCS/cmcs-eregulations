import logging
import os

from .exceptions import BackendInitException

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


# Base class for file backends
# Child classes are automatically registered when added to __init__.py
class FileBackend:
    @classmethod
    def get_backend(cls, backend: str, config: dict = {}) -> "FileBackend":
        try:
            logger.info("Requested file backend is \"%s\".", backend)
            backend_class = {subclass.backend: subclass for subclass in cls.__subclasses__()}[backend]
            logger.info("Found matching file backend class \"%s\".", str(backend_class))
            backend = backend_class(config)
            logger.info("Backend initialized successfully.")
            return backend
        except KeyError:
            backends = [subclass.backend for subclass in cls.__subclasses__()]
            supported = "'" + "', '".join(backends) + "'"
            raise BackendInitException(f"'{backend}' is not a valid backend. Supported backends are: {supported}.")

    def __init__(self, config: dict):
        pass

    def get_file(self, uri: str) -> bytes:
        raise NotImplementedError("get_file function not implemented")
