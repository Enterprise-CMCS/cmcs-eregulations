import os

import requests

from .backend import FileBackend
from .exceptions import BackendException


class WebBackend(FileBackend):
    backend = "web"

    def get_file(self, temp_directory: str, uri: str) -> str:
        try:
            resp = requests.get(uri, timeout=60)
            if resp.status_code != 200:
                raise BackendException(f"GET request failed with a {resp.status_code} code: '{resp.content}'")
            file_path = os.path.join(temp_directory, uri.split(r'/')[-1])
            file = open(file_path, 'wb')
            file.write(resp.content)
            return file_path
        except requests.exceptions.RequestException as e:
            raise BackendException(f"GET request failed: {str(e)}")
