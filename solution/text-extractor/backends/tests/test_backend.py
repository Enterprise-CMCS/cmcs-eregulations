import unittest

from backends import BackendInitException, FileBackend


class TestBackend(FileBackend):
    backend = "test"


class TestFileBackend(unittest.TestCase):
    def test_get_backend(self):
        backend = FileBackend.get_backend("test")
        self.assertIsInstance(backend, TestBackend)

    def test_no_backend(self):
        with self.assertRaises(BackendInitException):
            FileBackend.get_backend("unregistered")

    def test_no_get_file_function(self):
        backend = FileBackend.get_backend("test")
        with self.assertRaises(NotImplementedError):
            backend.get_file("fake_dir", "some_uri")
