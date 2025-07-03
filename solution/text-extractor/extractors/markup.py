# Markup Extractor
# This extractor handles HTML, XML, and similar markup formats.
# Generally, it attempts to extract the main text content while ignoring scripts, styles, and other non-content elements.
#
# It supports custom rules on a per-site basis by defining _extract_from_<hostname> methods.
# If no custom rule is defined or the custom rule fails, it falls back to generic extraction logic, starting with the <main>
# tag, then <article> or <section> tags, and finally the entire body.

import os
import logging
from urllib.parse import urlparse
import warnings

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from .extractor import Extractor

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class MarkupExtractor(Extractor):
    file_types = ("html", "xml", "javascript", "asp", "php")

    def _extract(self, file: bytes) -> str:
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)  # Hide unnecessary warning about parsing XML
        soup = BeautifulSoup(file, "html.parser")  # Use html.parser to avoid lxml dependency (has M1 issues)
        warnings.resetwarnings()

        # Remove unwanted tags
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
            tag.decompose()

        # If the file is retrieved using the web backend, use URI to check for existance of custom extraction rules
        if self.config.get("backend", "web") == "web":
            try:
                uri = self.config["uri"]
                hostname = urlparse(uri).hostname or ""
                hostname = hostname[4:] if hostname.startswith("www.") else hostname
                func_name = "_extract_from_" + hostname.replace(".", "_")
                logger.info("Found hostname '%s'. Attempting to use custom rules in function: '%s'.", hostname, func_name)
                return getattr(self, func_name)(soup)
            except Exception:
                # If the custom extraction function does not exist or fails to find text, we will handle it below
                logger.warning("Failed to extract using custom hostname-based rules. Falling back to default extraction logic.")

        # If no custom extraction rule is defined for this domain or text wasn't found, attempt to use default extraction logic

        # Fallback 1: Look for content in a <main> tag first
        try:
            logger.info("Fallback 1: Attempting to extract text from <main> tag.")
            return soup.find("main").get_text(" ")
        except Exception:
            # If the <main> tag is not found or fails to extract text, fallback to other methods
            logger.warning("Failed to extract text from <main> tag.")

        # Fallback 2: look for <article> or <section> tags
        try:
            logger.info("Fallback 2: Attempting to extract text from <article> or <section> tags.")
            candidates = soup.find_all(["article", "section"], recursive=True) or None
            return " ".join(candidate.get_text(" ") or "" for candidate in candidates).strip()
        except Exception:
            logger.warning("Failed to extract text from <article> or <section> tags.")

        # Fallback 3: use the page's entire body
        logger.info("Fallback 3: Attempting to extract text from the entire <body> tag.")
        body = soup.body or soup
        return body.get_text(" ")

    # Extract text from uscode.house.gov pages
    def _extract_from_uscode_house_gov(self, soup: BeautifulSoup) -> str:
        # Find the main content area, which is inside <div id="docViewer">
        content = soup.find("div", id="docViewer")
        for i in content.find_all("div", class_="jumpTo"):  # Remove "jump to" links
            i.decompose()
        return content.get_text(" ")

    # Extract text from gao.gov pages
    def _extract_from_gao_gov(self, soup: BeautifulSoup) -> str:
        # GAO.gov pages have the main content in a <div id="block-gao-uswds-content">
        content = soup.find("div", id="block-gao-uswds-content")
        return content.get_text(" ")

    # Extract text from cmsgov.github.io pages
    def _extract_from_cmsgov_github_io(self, soup: BeautifulSoup) -> str:
        # cmsgov.github.io pages have the main content in an <article> tag
        content = soup.find("article", id="content")
        return content.get_text(" ")

    def _extract_from_cms_gov(self, soup: BeautifulSoup) -> str:
        # Some cms.gov pages have the main content in a <div id="block-cms-evo-content">
        content = soup.find("div", id="block-cms-evo-content")
        return content.get_text(" ")
