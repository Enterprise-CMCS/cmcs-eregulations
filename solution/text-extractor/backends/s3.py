import os

import boto3
import botocore.exceptions

from .backend import FileBackend
from .exceptions import BackendException, BackendInitException


class S3Backend(FileBackend):
    backend = "s3"

    def __init__(self, config: dict):
        try:
            if not config['aws']['use_lambda']:
                self.aws_access_key_id = config["aws"]["aws_access_key_id"]
                self.aws_secret_access_key = config["aws"]["aws_secret_access_key"]
            self.aws_storage_bucket_name = config["aws"]["aws_storage_bucket_name"]
        except KeyError:
            raise BackendInitException("the S3 backend requires 'use_lambda', 'aws_access_key_id', 'aws_secret_access_key', "
                                       "and 'aws_storage_bucket_name' in the 'aws' key of the JSON POST body.")
        try:
            if config['aws']['use_lambda']:
                self.client = boto3.client('s3', region_name="us-east-1")
            else:
                self.client = boto3.client(
                    "s3",
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                )
        except Exception as e:
            raise BackendInitException(f"failed to initialize AWS client: {str(e)}")

    def get_file(self, temp_directory: str, uri: str) -> str:
        try:
            file_path = os.path.join(temp_directory, uri.split('/')[-1])
            try:
                with open(file_path, 'wb') as f:
                    self.client.download_fileobj(self.aws_storage_bucket_name, uri, f)
            except Exception as e:
                raise BackendException(e)
            return file_path
        except botocore.exceptions.ClientError as e:
            raise BackendException(f"S3 client error: {str(e)}")
        except Exception as e:
            raise BackendException(f"the read operation unexpectedly failed: {str(e)}")
