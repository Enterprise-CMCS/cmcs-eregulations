
import textract

from .extractor import Extractor


class OfficeExtractor(Extractor):
    file_types = (
        'docx',
        'xls',
        'xlsx',
        'xlsm',
        'pptx',
    )

    def extract(self, file_path: str) -> str:
        # Treat xlsm files as xlsx for textract
        if self.file_type == "xlsm":
            self.file_type = "xlsx"

        text = textract.process(file_path, extension=self.file_type)

        # cleans up weird characters
        text = text.decode('utf-8').encode('ascii', 'ignore').decode('utf-8')

        return text
