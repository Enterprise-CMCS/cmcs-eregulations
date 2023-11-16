import io
from .extractor import Extractor
import textract
import re
import docx
class WordExractor(Extractor):
    file_types = (
                  'docx',
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                  'doc'
                  )

    def extract(self, file: bytes, file_path) -> str:
        text = textract.process(file_path)
        # cleans up weird characters
        line = re.sub(r'(\n)+', ' ', text.decode('utf-8').encode('ascii', 'ignore').decode('utf-8'))
        # replaces multiple spaces with single space
        line = re.sub(r'(\s)', ' ', line)
        return line

