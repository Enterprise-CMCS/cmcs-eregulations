import re

import textract

from .extractor import Extractor


class WordExractor(Extractor):
    file_types = (
                  'docx',
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                  )

    def extract(self, file_path: str) -> str:

        try:
            text = textract.process(file_path)
        except Exception as e:
            print(e)

        # cleans up weird characters
        line = re.sub(r'(\n)+', ' ', text.decode('utf-8').encode('ascii', 'ignore').decode('utf-8'))
        # replaces multiple spaces with single space
        line = re.sub(r'(\s)', ' ', line)
        return line
