# About

This Lambda function is run to extract text from a variety of file types and POST it to an arbitrary URL. The purpose of this is to support eRegs' full-text search goals as our users begin uploading files to the policy repository.

# Supported file types

The text extractor supports the following file types. File types that are planned but not yet implemented are not checked.

- [x] Plain text
- [ ] HTML and XML
- [ ] PDF
- [ ] Images (png, jpeg, gif, etc.)
- [ ] Microsoft Word (doc and docx)
- [ ] Microsoft Excel (xls and xlsx)
- [ ] Microsoft Outlook (msg)
- [ ] Microsoft PowerPoint (ppt and pptx)

# Running locally

This project uses Lambda docker containers to further the goal of making our deployed and development environments match. However, there are limitations of these containers:

- They do not natively emulate API Gateway.
- They do not accept more than one request at a time.

These limitations are being worked on, but in the meantime there is an additional dependency found in the [lambda-proxy](../lambda-proxy) directory. This program is copied into the Docker container on build and is transparent to the user. It takes standard HTTP requests/responses and translates them into the type of JSON-based requests/responses that Lambda functions expect. In effect, this proxy partially emulates API Gateway. See [here](https://docs.aws.amazon.com/lambda/latest/dg/urls-invocation.html) for more information on Lambda request/response payload structure.

The extractor will be automatically started when `docker-compose up -d --build` is run because eRegs depends on it.

No further action is required, but if you want the code to hot-reload during development, you may install `watchfiles` with `pip3 install watchfiles` and then run `make watch-text-extractor`.

# Request structure

To run the text extractor, send a JSON POST request with the following structure:

```jsonc
{
    "id": 1,                                 // The eRegs database ID of the object to update
    "uri": "object_uri",                     // The web URL or object name to extract text from
    "post_url": "https://api-url-here/",     // The API URL to POST the text to
    "post_username": "xxxxx",                // Optional - include if API requires authentication
    "post_password": "xxxxx",                // Optional - include if API requires authentication
    "backend": "s3",                         // Optional - defaults to 'web'
    // Only include if using the S3 backend
    "s3": {
        "aws_access_key_id": "xxxxxx",       // The access key for the AWS bucket
        "aws_secret_access_key": "xxxxxx",   // The AWS secret key
        "aws_storage_bucket_name": "xxxxxx"  // The name of the bucket to retrieve the object from
    }
}
```

It is recommended to run this asynchronously as it could take time to run, up to several minutes for large PDF files, for example.

# Response structure

When the function completes, it will send the text and ID back to the `post_url` specified in the request as a JSON POST request formatted like:

```jsonc
{
    "id": 1,          // The eRegs database ID specified in the request
    "text": "xxxxxx"  // The text extracted   
}
```

Future iterations may include POSTing error messages to eRegs if they occur, but for now errors will be recorded in logs only and no POST will be sent.

# Creating a new file backend

The text extractor is designed to be easily extensible to add new file backends and file type support.

To add a new file backend, create a new file in the `backends` directory and create a class inheriting from the `FileBackend` class. Then add the new backend class to `__init__.py` to register it, like so:

_`backends/sample.py`_:
```python
from .backend import FileBackend
from .exceptions import BackendException

class SampleBackend(FileBackend):
    backend = "sample"

    def get_file(self, uri: str) -> bytes:
        try:
            return ... do something to get the file ...
        except SomeException as e:
            raise BackendException(f"Failed to retrieve the file: {str(e)}")
```

_`backends/__init__.py`_:
```python
.... etc ...

# Add your file extractors here to initialize them
.... etc ...
from .sample import SampleBackend
.... etc ...
```

The backend is now registered and will be automatically instantiated when `"backend": "sample"` is included in the POST request.

# Creating a new text extractor

To add support for a new file type (or group of file types), create a new file in the `extractors` directory and create a class inheriting from the `Extractor` class. Then add the new extractor class to `__init__.py` to register it, like so:

_`extractors/sample.py`_:
```python
from .extractor import Extractor

class SampleExtractor(Extractor):
    file_types = ("sample/mimetype1", "sample/mimetype2", ...)

    def extract(self, file: bytes) -> str:
        return ...extract text here...
```

_`extractors/__init__.py`_:
```python
.... etc ....

# Add your file extractors here to initialize them
.... etc ....
from .sample import SampleExtractor
.... etc ....
```

The extractor is now registered and will be automatically instantiated when a file has one of the MIME types listed in `file_types`.
