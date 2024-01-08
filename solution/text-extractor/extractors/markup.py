import warnings

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from .extractor import Extractor


class MarkupExtractor(Extractor):
    file_types = ("html", "htm", "xhtml", "xml")

    def extract(self, file: bytes) -> str:
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        extractor = BeautifulSoup(file, "html.parser")  # Use html.parser to avoid lxml dependency (has M1 issues)
        for i in extractor(["script", "style"]):
            i.decompose()  # Remove <script> and <style> inline tags
        return extractor.get_text(" ")
