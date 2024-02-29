import re

from olefile import OleFileIO as ofio

from .extractor import Extractor


class BinaryExtractor(Extractor):
    file_types = ("application/msword",)

    def _extract(self, file: bytes) -> str:
        #  Solution taken from here https://stackoverflow.com/questions/64397811/reading-a-doc-file-in-memory.  Doc files
        #  This is used for binary types.  So far just .doc but might include .xls.  We shall see.
        file_path = self._write_file(file)
        with open(file_path, 'rb') as file:
            f = ofio(file)
            data = f.openstream('WordDocument').read()
            data = data.decode('latin-1', errors='ignore')
            data = (re.sub(r'[^\x0A,\u00c0-\u00d6,\u00d8-\u00f6,\u00f8-\u02af,\u1d00-\u1d25,\u1d62-\u1d65,\u1d6b-\u1d77,' +
                           r'\u1d79-\u1d9a,\u1e00-\u1eff,\u2090-\u2094,\u2184-\u2184,\u2488-\u2490,\u271d-\u271d,' +
                           r'\u2c60-\u2c7c,\u2c7e-\u2c7f,\ua722-\ua76f,\ua771-\ua787,\ua78b-\ua78c,\ua7fb-\ua7ff,' +
                           r'\ufb00-\ufb06,\x20-\x7E]', r'*', data))
            p = re.compile(r'\*{300,433}((?:[^*]|\*(?!\*{14}))+?)\*{15,}')
            result = (re.findall(p, data))
            result = result[0].replace('*', '')
            return str(result)
