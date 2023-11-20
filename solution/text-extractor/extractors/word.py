import re

import textract

from .extractor import Extractor


class WordExractor(Extractor):
    file_types = (
                  'docx',
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                  'doc'
                  )

    def extract(self, file_path: str) -> str:
        print(file_path)
        import subprocess
        import os
        try:
            # subprocess.call(['lowriter', '--headless', '--convert-to', 'docx', file_path])
            catdoc_cmd = ['catdoc', '-w' , file_path]
            text = ''
            catdoc_process = subprocess.Popen(catdoc_cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            for line in catdoc_process.stdout:
                text = text + line
                print(line)
        except Exception as e:
            print(e)

        # cleans up weird characters
        line = re.sub(r'(\n)+', ' ', text.decode('utf-8').encode('ascii', 'ignore').decode('utf-8'))
        # replaces multiple spaces with single space
        line = re.sub(r'(\s)', ' ', line)
        return line
