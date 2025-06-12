import logging
import os
import time
from urllib import robotparser
from urllib.parse import urlsplit

import requests

from .backend import FileBackend
from .exceptions import BackendException

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class WebBackend(FileBackend):
    backend = "web"

    _retry_timeout = 30
    _user_agent = "CMCSeRegsTextExtractorBot/1.0"

    def __init__(self, config: dict):
        self._ignore_robots = config.get("ignore_robots_txt", False)
        self._headers = requests.utils.default_headers()
        self._headers["User-Agent"] = self._user_agent

    def get_file(self, uri: str) -> bytes:
        logger.info("Retrieving file \"%s\" using 'web' backend.", uri)

        # Use robots.txt to determine if we can crawl the URL
        if not self._ignore_robots:
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

        # Loop until the lambda times out, max of 15 mins
        while True:
            try:
                logger.debug("Sending GET request to %s with headers: %s", uri, str(self._headers))
                resp = requests.get(uri, timeout=60, headers=self._headers)
            except requests.exceptions.Timeout:
                logger.warning("GET request timed out. Retrying in %i seconds.", self.retry_timeout)
                time.sleep(self.retry_timeout)
                continue
            except requests.exceptions.RequestException as e:
                raise BackendException(f"GET request failed: {str(e)}")

            if resp.status_code == requests.codes.OK:
                return resp.content
            elif "Retry-After" in resp.headers:
                retry = int(resp.headers["Retry-After"])
                logger.warning("Received a %i response with a 'Retry-After' of %i seconds.", resp.status_code, retry)
                time.sleep(retry)
                continue
            elif resp.status_code == requests.codes.TOO_MANY:
                logger.warning("Got a 'too many requests' error for \"%s\". Retrying in %i seconds.", uri, self.retry_timeout)
                time.sleep(self.retry_timeout)
                continue
            else:
                raise BackendException(f"GET request failed with a {resp.status_code} code: '{resp.content}'")
