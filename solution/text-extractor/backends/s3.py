import logging
import os

import boto3
import botocore.exceptions

from .backend import FileBackend
from .exceptions import BackendException, BackendInitException

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class S3Backend(FileBackend):
    backend = "s3"

    def __init__(self, config: dict):
        logger.info("Initializing S3 backend.")
        try:
            if not config['aws']['use_lambda']:
                logger.info("'use_lambda' set to false, retrieving keys from config.")
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

    def get_file(self, uri: str) -> bytes:
        logger.info("Retrieving file \"%s\" from bucket \"%s\".", uri, self.aws_storage_bucket_name)
        try:
            obj = self.client.get_object(Bucket=self.aws_storage_bucket_name, Key=uri)
            return obj["Body"].read()
        except botocore.exceptions.ClientError as e:
            raise BackendException(f"S3 client error: {str(e)}")
        except Exception as e:
            raise BackendException(f"the read operation unexpectedly failed: {str(e)}")
