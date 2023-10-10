import boto3
import requests


class BackendInitException(Exception):
    pass


class BackendException(Exception):
    pass


class FileBackend:
    @classmethod
    def get_backend(cls, backend, get_params, post_params):
        try:
            return {subclass.backend: subclass for subclass in cls.__subclasses__()}[backend](get_params, post_params)
        except KeyError:
            backends = [subclass.backend for subclass in cls.__subclasses__()]
            supported = "'" + "', '".join(backends) + "'"
            raise BackendInitException(f"'{backend}' is not a valid backend. Supported backends are: {supported}.")

    def __init__(self, get_params, post_params):
        pass

    def get_file(self):
        raise NotImplementedError


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
        self.client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_acces_key,
        )

    def __del__(self):
        self.client.destroy()

    def get_file(self, uri):
        return self.client.get_object(Bucket=self.aws_storage_bucket_name, key=uri)


class WebBackend(FileBackend):
    backend = "web"

    def get_file(self, uri):
        resp = requests.get(uri)
        if resp.status_code != 200:
            raise BackendException(f"GET failed with a {resp.status_code} code: '{resp.content}'")
        return resp.content
