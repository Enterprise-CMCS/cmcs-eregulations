import unittest
from unittest.mock import Mock, patch
from urllib.robotparser import RobotFileParser
import urllib.request
import urllib.error

import requests

from backends import (
    BackendException,
    FileBackend,
    WebBackend,
)

SUCCESS_MOCK = Mock(
    status_code=200,
    content=b"This is some content",
    headers={},
)


class TestWebBackend(unittest.TestCase):
    def test_create_backend(self):
        backend = FileBackend.get_backend("web")
        self.assertIsInstance(backend, WebBackend)

    def _test_get_success(self, mock_read, mock_can_fetch, mock_get):
        backend = FileBackend.get_backend("web")
        data = backend.get_file("https://some_url/file.txt")
        self.assertEqual(data, b"This is some content")

    def _test_get_failure(self, mock_read, mock_can_fetch, mock_get):
        backend = FileBackend.get_backend("web")
        with self.assertRaises(BackendException):
            backend.get_file("https://some_url/file.txt")

    @patch.object(RobotFileParser, "read", return_value=None)
    @patch.object(RobotFileParser, "can_fetch", return_value=True)
    @patch.object(requests, "get", return_value=SUCCESS_MOCK)
    def test_get_file(self, *args):
        self._test_get_success(*args)

    @patch.object(RobotFileParser, "read", return_value=None)
    @patch.object(RobotFileParser, "can_fetch", return_value=False)
    @patch.object(requests, "get", return_value=SUCCESS_MOCK)
    def test_fetch_not_allowed(self, *args):
        self._test_get_failure(*args)

    @patch.object(RobotFileParser, "read", return_value=None)
    @patch.object(RobotFileParser, "can_fetch", return_value=True)
    @patch.object(requests, "get")
    def test_bad_url(self, mock_get, mock_can_fetch, mock_read):
        mock_response = Mock(status_code=404, content=b"File not found!", headers={})
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_get.return_value = mock_response
        self._test_get_failure(mock_read, mock_can_fetch, mock_get)

    @patch.object(RobotFileParser, "read", return_value=None)
    @patch.object(RobotFileParser, "can_fetch", return_value=True)
    @patch.object(requests, "get", side_effect=requests.exceptions.RequestException("Something unexpected happened"))
    def test_request_exception(self, *args):
        self._test_get_failure(*args)

    @patch.object(RobotFileParser, "read", return_value=None)
    @patch.object(RobotFileParser, "can_fetch", return_value=True)
    @patch.object(requests, "get", side_effect=[
        requests.exceptions.Timeout("Timeout occured"),
        Mock(status_code=200, content=b"This is some content", headers={}),
    ])
    def test_requests_timeout(self, *args):
        self._test_get_failure(*args)

    @patch.object(urllib.request, "urlopen", return_value=Mock(status=200, read=lambda: b"User-agent: *\nAllow: /\n"))
    @patch.object(requests, "get", return_value=SUCCESS_MOCK)
    def test_get_robots_txt_200(self, *args):
        backend = FileBackend.get_backend("web")
        data = backend.get_file("https://example.com/test.txt")
        self.assertEqual(data, b"This is some content")

    @patch.object(urllib.request, "urlopen", side_effect=urllib.error.HTTPError(
        url="https://example/robots.txt",
        code=404,
        msg="Not Found",
        hdrs=None,
        fp=None
    ))
    @patch.object(requests, "get", return_value=SUCCESS_MOCK)
    def test_get_robots_txt_404(self, *args):
        backend = FileBackend.get_backend("web")
        data = backend.get_file("https://example.com/test.txt")
        self.assertEqual(data, b"This is some content")

    @patch.object(requests, "head", return_value=Mock(status_code=403))
    def test_get_robots_txt_forbidden(self, *args):
        backend = FileBackend.get_backend("web")
        with self.assertRaises(BackendException):
            backend.get_file("https://example.com/test.txt")
