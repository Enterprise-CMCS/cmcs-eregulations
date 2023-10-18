import unittest

import mock
import requests

from backends import (
    BackendException,
    FileBackend,
    WebBackend,
)


class TestWebBackend(unittest.TestCase):
    def test_create_backend(self):
        backend = FileBackend.get_backend("web")
        self.assertIsInstance(backend, WebBackend)

    def test_get_file(self):
        with mock.patch.object(requests, "get") as get_mock:
            get_mock.return_value = mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.content = b"This is some content"

            backend = FileBackend.get_backend("web")
            file = backend.get_file("some_url")
            self.assertEqual(file, b"This is some content")

    def test_bad_url(self):
        with mock.patch.object(requests, "get") as get_mock:
            get_mock.return_value = mock_response = mock.Mock()
            mock_response.status_code = 404
            mock_response.content = b"File not found!"

            backend = FileBackend.get_backend("web")
            with self.assertRaises(BackendException):
                backend.get_file("some_url")

    def test_request_exception(self):
        with mock.patch.object(requests, "get") as get_mock:
            get_mock.return_value = mock_response = mock.Mock()
            get_mock.side_effect = requests.exceptions.RequestException("Something happened")
            mock_response.status_code = 200
            mock_response.content = b"This is some content"

            backend = FileBackend.get_backend("web")
            with self.assertRaises(BackendException):
                backend.get_file("some_url")
