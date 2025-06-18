import logging
import os
from urllib import robotparser
from urllib.parse import urlsplit

import requests

from .backend import FileBackend
from .exceptions import BackendException

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class WebBackend(FileBackend):
    backend = "web"

    _user_agent = "CMCSeRegsTextExtractorBot/1.0"

    def __init__(self, config: dict):
        self._ignore_robots = config.get("ignore_robots_txt", False)
        self._headers = requests.utils.default_headers()
        self._headers["User-Agent"] = self._user_agent

    def get_file(self, uri: str) -> bytes:
        logger.info("Retrieving file \"%s\" using 'web' backend.", uri)

        # Use robots.txt to determine if we can crawl the URL
        if self._ignore_robots:
            logger.debug("Ignoring robots.txt for \"%s\".", uri)
        else:
            logger.debug("Checking robots.txt for \"%s\".", uri)
            if not uri.startswith(("http://", "https://")):
                raise BackendException(f"Invalid URL scheme for robots.txt: {uri}")
            # Parse the URL to construct the robots.txt path
            path = urlsplit(uri)
            path = f"{path.scheme}://{path.netloc}/robots.txt"
            robots_parser = robotparser.RobotFileParser()
            robots_parser.set_url(path)
            robots_parser.read()
            if not robots_parser.can_fetch(self._user_agent, uri):
                raise BackendException(f"robots.txt has disallowed crawling of \"{uri}\"")

        # Attempt to retrieve the file
        try:
            logger.debug("Sending GET request to %s with headers: %s", uri, str(self._headers))
            resp = requests.get(uri, timeout=60, headers=self._headers)
            resp.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        except requests.exceptions.Timeout:
            raise BackendException("GET request timed out")
        except requests.exceptions.RequestException as e:
            raise BackendException(f"GET request failed: {str(e)}")
        except requests.exceptions.HTTPError as e:
            raise BackendException(f"GET request failed with HTTP error: {str(e)}")

        logger.debug("Received response with status code %i.", resp.status_code)
        return resp.content
