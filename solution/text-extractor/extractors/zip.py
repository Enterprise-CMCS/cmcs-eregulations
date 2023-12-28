import logging
import os
import zipfile
from tempfile import TemporaryDirectory

from .extractor import Extractor

logger = logging.getLogger(__name__)


class ZipExtractor(Extractor):
    file_types = ("zip",)

    def extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        text = ""

        with TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                zip_file.extractall(temp_dir)

            for root, directories, files in os.walk(temp_dir):
                for file_name in files:
                    file_name.lower().split('.')[-1]
                    file_path = os.path.abspath(os.path.join(root, file_name))
                    with open(file_path, "rb") as f:
                        data = f.read()
                    text += f" {file_name} {self._extract_embedded(file_name, data)}"

        return text
