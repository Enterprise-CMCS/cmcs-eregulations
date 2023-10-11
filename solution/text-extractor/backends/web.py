import requests

from .backend import FileBackend
from .exceptions import BackendException


class WebBackend(FileBackend):
    backend = "web"

    def get_file(self, uri: str) -> bytes:
        resp = requests.get(uri)
        if resp.status_code != 200:
            raise BackendException(f"GET failed with a {resp.status_code} code: '{resp.content}'")
        return resp.content
