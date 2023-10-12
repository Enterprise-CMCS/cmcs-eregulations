import requests

from .backend import FileBackend
from .exceptions import BackendException


class WebBackend(FileBackend):
    backend = "web"

    def get_file(self, uri: str) -> bytes:
        try:
            resp = requests.get(uri, timeout=60)
            if resp.status_code != 200:
                raise BackendException(f"GET request failed with a {resp.status_code} code: '{resp.content}'")
            return resp.content
        except requests.exceptions.RequestException as e:
            raise BackendException(f"GET request failed: {str(e)}")
