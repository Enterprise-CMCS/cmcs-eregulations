import logging
import os
import zipfile
from tempfile import TemporaryDirectory

from .extractor import Extractor

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class ZipExtractor(Extractor):
    file_types = ("zip",)

    def _extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        text = ""

        # Before doing anything else, determine if it's really a zip or an Office file
        with zipfile.ZipFile(file_path, "r") as zip_file:
            names = zip_file.namelist()
            if "word/document.xml" in names:
                logger.info("Zip file is really a Microsoft Word file.")
                extractor = Extractor.get_extractor("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                return extractor.extract(file)
            elif "xl/workbook.xml" in names:
                logger.info("Zip file is really a Microsoft Excel file.")
                extractor = Extractor.get_extractor("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                return extractor.extract(file)
            elif "ppt/presentation.xml" in names:
                logger.info("Zip file is really a Microsoft PowerPoint file.")
                extractor = Extractor.get_extractor("application/vnd.openxmlformats-officedocument.presentationml.presentation")
                return extractor.extract(file)

        with TemporaryDirectory() as temp_dir:
            logger.debug("Extracting zip file contents to temporary directory.")
            with zipfile.ZipFile(file_path, "r") as zip_file:
                zip_file.extractall(temp_dir)

            for root, directories, files in os.walk(temp_dir):
                for file_name in files:
                    logger.debug("Extracting text from file \"%s\".", file_name)
                    file_name.lower().split('.')[-1]
                    file_path = os.path.abspath(os.path.join(root, file_name))
                    with open(file_path, "rb") as f:
                        data = f.read()
                    text += f" {file_name} {self._extract_embedded(file_name, data)}"

        return text
