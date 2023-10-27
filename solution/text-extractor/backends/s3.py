import boto3
import botocore.exceptions

from .backend import FileBackend
from .exceptions import BackendException, BackendInitException


class S3Backend(FileBackend):
    backend = "s3"

    def __init__(self, config: dict):
        try:
            self.aws_access_key_id = config["s3"]["aws_access_key_id"]
            self.aws_secret_access_key = config["s3"]["aws_secret_access_key"]
            self.aws_storage_bucket_name = config["s3"]["aws_storage_bucket_name"]
        except KeyError:
            raise BackendInitException("the S3 backend requires 'aws_access_key_id', 'aws_secret_access_key', "
                                       "and 'aws_storage_bucket_name' in the 's3' key of the JSON POST body.")
        try:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
        except Exception as e:
            raise BackendInitException(f"failed to initialize AWS client: {str(e)}")

    def get_file(self, uri: str) -> bytes:
        try:
            obj = self.client.get_object(Bucket=self.aws_storage_bucket_name, Key=uri)
            return obj["Body"].read()
        except botocore.exceptions.ClientError as e:
            raise BackendException(f"S3 client error: {str(e)}")
        except Exception as e:
            raise BackendException(f"the read operation unexpectedly failed: {str(e)}")
