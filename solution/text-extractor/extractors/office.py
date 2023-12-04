import re

import textract

from .extractor import Extractor


class OfficeExtractor(Extractor):
    file_types = (
        'docx',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls',
        'xlsx',
        'pptx',
    )

    def extract(self, file_path: str) -> str:
        text = textract.process(file_path)

        # cleans up weird characters
        line = re.sub(r'(\n)+', ' ', text.decode('utf-8').encode('ascii', 'ignore').decode('utf-8'))
        # replaces multiple spaces with single space, and removes surrounding spaces
        line = re.sub(r'\s+', ' ', line).strip()
        return line
