import unittest
from unittest.mock import Mock, patch
from urllib import robotparser

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

    def _test_get_success(self, mock_get_robots_txt, mock_can_fetch, mock_get):
        backend = FileBackend.get_backend("web")
        backend.retry_timeout = 0.1
        data = backend.get_file("https://some_url/file.txt")
        self.assertEqual(data, b"This is some content")

    def _test_get_failure(self, mock_get_robots_txt, mock_can_fetch, mock_get):
        backend = FileBackend.get_backend("web")
        backend.retry_timeout = 0.1
        with self.assertRaises(BackendException):
            backend.get_file("https://some_url/file.txt")

    @patch.object(WebBackend, "_get_robots_txt", return_value=None)
    @patch.object(WebBackend, "_can_fetch", return_value=True)
    @patch.object(requests, "get", return_value=SUCCESS_MOCK)
    def test_get_file(self, *args):
        self._test_get_success(*args)

    @patch.object(WebBackend, "_get_robots_txt", side_effect=Exception("Robots.txt failed to download"))
    @patch.object(WebBackend, "_can_fetch", return_value=True)
    @patch.object(requests, "get", return_value=SUCCESS_MOCK)
    def test_robots_txt_failure(self, *args):
        self._test_get_failure(*args)

    @patch.object(WebBackend, "_get_robots_txt", return_value=None)
    @patch.object(WebBackend, "_can_fetch", return_value=False)
    @patch.object(requests, "get", return_value=SUCCESS_MOCK)
    def test_fetch_not_allowed(self, *args):
        self._test_get_failure(*args)

    @patch.object(WebBackend, "_get_robots_txt", return_value=None)
    @patch.object(WebBackend, "_can_fetch", return_value=True)
    @patch.object(requests, "get", return_value=Mock(status_code=404, content=b"File not found!", headers={}))
    def test_bad_url(self, *args):
        self._test_get_failure(*args)

    @patch.object(WebBackend, "_get_robots_txt", return_value=None)
    @patch.object(WebBackend, "_can_fetch", return_value=True)
    @patch.object(requests, "get", side_effect=requests.exceptions.RequestException("Something unexpected happened"))
    def test_request_exception(self, *args):
        self._test_get_failure(*args)

    @patch.object(WebBackend, "_get_robots_txt", return_value=None)
    @patch.object(WebBackend, "_can_fetch", return_value=True)
    @patch.object(requests, "get", side_effect=[
        requests.exceptions.Timeout("Timeout occured"),
        Mock(status_code=200, content=b"This is some content", headers={}),
    ])
    def test_requests_timeout(self, *args):
        self._test_get_success(*args)

    @patch.object(WebBackend, "_get_robots_txt", return_value=None)
    @patch.object(WebBackend, "_can_fetch", return_value=True)
    @patch.object(requests, "get", side_effect=[
        Mock(status_code=503, content=b"Unavailable right now", headers={"Retry-After": 1}),
        Mock(status_code=200, content=b"This is some content", headers={}),
    ])
    def test_retry_after(self, *args):
        self._test_get_success(*args)

    @patch.object(WebBackend, "_get_robots_txt", return_value=None)
    @patch.object(WebBackend, "_can_fetch", return_value=True)
    @patch.object(requests, "get", side_effect=[
        Mock(status_code=429, content=b"Too many requests! But no 'retry-after'.", headers={}),
        Mock(status_code=200, content=b"This is some content", headers={}),
    ])
    def test_too_many_requests(self, *args):
        self._test_get_success(*args)

    @patch.object(requests, "head", return_value=Mock(status_code=200))
    @patch.object(robotparser.RobotFileParser, "read", return_value=None)
    def test_get_robots_txt_200(self, *args):
        backend = FileBackend.get_backend("web")
        backend._get_robots_txt("https://example/robots.txt")
        self.assertEqual(backend._ignore_robots, False)

    @patch.object(requests, "head", return_value=Mock(status_code=404))
    @patch.object(robotparser.RobotFileParser, "read", return_value=None)
    def test_get_robots_txt_404(self, *args):
        backend = FileBackend.get_backend("web")
        backend._get_robots_txt("https://example/robots.txt")
        self.assertEqual(backend._ignore_robots, True)

    @patch.object(requests, "head", return_value=Mock(status_code=123))
    @patch.object(robotparser.RobotFileParser, "read", return_value=None)
    def test_get_robots_txt_other_error(self, *args):
        backend = FileBackend.get_backend("web")
        with self.assertRaises(BackendException):
            backend._get_robots_txt("https://example/robots.txt")
