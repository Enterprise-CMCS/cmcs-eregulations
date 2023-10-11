import boto3

from . import FileBackend
from .exceptions import BackendInitException, BackendException


class S3Backend(FileBackend):
    backend = "s3"

    def __init__(self, get_params, post_params):
        try:
            self.aws_access_key_id = post_params["aws_access_key_id"]
            self.aws_secret_acces_key = post_params["aws_secret_access_key"]
            self.aws_storage_bucket_name = post_params["aws_storage_bucket_name"]
        except KeyError:
            raise BackendInitException("The S3 backend requires 'aws_access_key_id', 'aws_secret_access_key', "
                                       "and 'aws_storage_bucket_name' in the JSON POST body.")
        try:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_acces_key,
            )
        except Exception as e:
            raise BackendInitException(f"Failed to initialize AWS client: {str(e)}")

    def __del__(self):
        self.client.destroy()

    def get_file(self, uri):
        try:
            return self.client.get_object(Bucket=self.aws_storage_bucket_name, key=uri)
        except Exception as e:
            raise BackendException(str(e))
