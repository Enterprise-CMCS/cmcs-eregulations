import unittest
from unittest.mock import patch

import boto3
from moto import mock_aws

from backends import (
    BackendException,
    BackendInitException,
    FileBackend,
    S3Backend,
)


class TestS3Backend(unittest.TestCase):
    BUCKET_NAME = "some_bucket"
    FILE_NAME = "some_file"
    FILE_BODY = b"This is some content"

    POST_PARAMS = {
        "aws": {
            "use_lambda": True,
            "aws_access_key_id": "some_id",
            "aws_secret_access_key": "some_key",
            "aws_storage_bucket_name": BUCKET_NAME,
        },
    }

    def setUp(self):
        self.mock = mock_aws()
        self.mock.start()

        conn = boto3.resource("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=self.BUCKET_NAME)
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.put_object(Bucket=self.BUCKET_NAME, Key="some_file", Body=self.FILE_BODY)

    def test_create_backend(self):
        backend = FileBackend.get_backend("s3", self.POST_PARAMS)
        self.assertIsInstance(backend, S3Backend)

    def test_required_keys(self):
        with self.assertRaises(BackendInitException):
            S3Backend({})

        for i in ["use_lambda", "aws_access_key_id", "aws_secret_access_key", "aws_storage_bucket_name"]:
            params = self.POST_PARAMS.copy()
            del params["aws"][i]
            with self.assertRaises(BackendInitException):
                S3Backend(params)

    @patch.object(boto3, "client", side_effect=Exception("Something happened"))
    def test_client_create_exception(self, *args):
        with self.assertRaises(BackendInitException):
            S3Backend(self.POST_PARAMS)

    def test_get_file(self):
        backend = S3Backend(self.POST_PARAMS)
        data = backend.get_file(self.FILE_NAME)
        self.assertEqual(data, self.FILE_BODY)

    def test_bad_key(self):
        backend = S3Backend(self.POST_PARAMS)
        with self.assertRaises(BackendException):
            backend.get_file("invalid_key")
