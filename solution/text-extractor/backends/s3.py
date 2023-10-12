import boto3
import botocore.exceptions

from .backend import FileBackend
from .exceptions import BackendException, BackendInitException


class S3Backend(FileBackend):
    backend = "s3"

    def __init__(self, post_params: dict):
        try:
            self.aws_access_key_id = post_params["aws_access_key_id"]
            self.aws_secret_access_key = post_params["aws_secret_access_key"]
            self.aws_storage_bucket_name = post_params["aws_storage_bucket_name"]
        except KeyError:
            raise BackendInitException("The S3 backend requires 'aws_access_key_id', 'aws_secret_access_key', "
                                       "and 'aws_storage_bucket_name' in the JSON POST body.")
        try:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
        except Exception as e:
            raise BackendInitException(f"Failed to initialize AWS client: {str(e)}")

    def __del__(self):
        self.client.destroy()

    def get_file(self, uri: str) -> bytes:
        try:
            obj = self.client.get_object(Bucket=self.aws_storage_bucket_name, Key=uri)
            return obj["Body"].read()
        except botocore.exceptions.ClientError as e:
            raise BackendException(f"S3 client error: {str(e)}")
        except Exception as e:
            raise BackendException(f"The read operation unexpectedly failed: {str(e)}")
