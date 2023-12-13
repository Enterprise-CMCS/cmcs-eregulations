import email
from tempfile import NamedTemporaryFile

from .exceptions import (
    ExtractorException,
    ExtractorInitException,
)
from .extractor import Extractor


class EmailExtractor(Extractor):
    file_types = ("eml",)

    def _extract_payload(self, message):
        payload = message.get_payload()

        if isinstance(payload, list):
            text = ""
            for i in payload:
                text += f" {self._extract_payload(i)}"
            return text

        if not message.get_filename() and message.get_content_type() == "text/plain":
            return f" {payload}"

        if not message.get_filename():
            return ""

        file_name = message.get_filename()
        file_type = file_name.lower().split('.')[-1]

        with NamedTemporaryFile(delete=False) as file:
            file.write(message.get_payload(decode=True))
            file.close()

            try:
                extractor = Extractor.get_extractor(file_type, self.config)
                text = extractor.extract(file.name)
            except ExtractorInitException as e:
                raise ExtractorException(f"failed to initialize extractor for attachment \"{file_name}\": {str(e)}")
            except ExtractorException as e:
                raise ExtractorException(f"failed to extract text for attachment \"{file_name}\": {str(e)}")
            except Exception as e:
                raise ExtractorException(f"extracting text for attachment \"{file_name}\" failed unexpectedly: {str(e)}")

            return f" {file_name} {text}"

    def extract(self, file_path: str) -> str:
        try:
            with open(file_path, "r") as f:
                msg = email.message_from_file(f)
        except Exception as e:
            raise ExtractorException(f"eml file failed to extract: {str(e)}")

        return self._extract_payload(msg)
