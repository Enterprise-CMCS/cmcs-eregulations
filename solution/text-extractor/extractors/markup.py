from bs4 import BeautifulSoup

from .extractor import Extractor


class MarkupExtractor(Extractor):
    file_types = ("html", "htm", "xhtml", "xml")

    def extract(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            data = f.read()
        extractor = BeautifulSoup(data, "html.parser")  # Use html.parser to avoid lxml dependency (has M1 issues)
        for i in extractor(["script", "style"]):
            i.decompose()  # Remove <script> and <style> inline tags
        return extractor.get_text(" ")
