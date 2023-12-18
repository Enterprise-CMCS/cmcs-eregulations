import os
import zipfile
from tempfile import TemporaryDirectory

from .exceptions import (
    ExtractorException,
    ExtractorInitException,
)
from .extractor import Extractor


class ZipExtractor(Extractor):
    file_types = ("zip",)

    def extract(self, file_path: str) -> str:
        full_text = ""

        with TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(file_path, "r") as zip_file:
                zip_file.extractall(temp_dir)

            for root, directories, files in os.walk(temp_dir):
                for file_name in files:
                    file_type = file_name.lower().split('.')[-1]
                    file_path = os.path.abspath(os.path.join(root, file_name))

                    try:
                        extractor = Extractor.get_extractor(file_type, self.config)
                        text = extractor.extract(file_path)
                        full_text += f" {file_name} {text}"
                    except ExtractorInitException as e:
                        raise ExtractorException(f"failed to initialize extractor for attachment \"{file_name}\": {str(e)}")
                    except ExtractorException as e:
                        raise ExtractorException(f"failed to extract text for attachment \"{file_name}\": {str(e)}")
                    except Exception as e:
                        raise ExtractorException(f"extracting text for attachment \"{file_name}\" failed unexpectedly: {str(e)}")

        return full_text
