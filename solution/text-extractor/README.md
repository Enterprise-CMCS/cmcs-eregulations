# About

This Lambda function is run to extract text from a variety of file types and POST it to an arbitrary URL. The purpose of this is to support eRegs' full-text search goals as our users begin uploading files to the policy repository.

# Supported file types

The text extractor supports the following file types. File types that are planned but not yet implemented are not checked.

- [x] Plain text (txt, multiple encodings supported)
- [x] HTML and XML (html, htm, xhtml, xml)
- [x] PDF
- [ ] Images (png, jpeg, gif, etc.)
- [x] Microsoft Word (doc and docx)
- [x] Microsoft Excel (xls and xlsx)
- [x] Microsoft Outlook (msg)
- [x] Generic Email (eml)
- [x] ZIP Archives
- [x] Microsoft PowerPoint 2007+ (pptx)
- [ ] Microsoft PowerPoint 97-2003 (ppt)
- [x] Rich Text Format (rtf)

# Running locally

This project uses Lambda docker containers to further the goal of making our deployed and development environments match. However, there are limitations of these containers:

- They do not natively emulate API Gateway.
- They do not accept more than one request at a time.

These limitations are being worked on, but in the meantime there is an additional dependency found in the [lambda-proxy](../lambda-proxy) directory. This program is copied into the Docker container on build and is transparent to the user. It takes standard HTTP requests/responses and translates them into the type of JSON-based requests/responses that Lambda functions expect. In effect, this proxy partially emulates API Gateway. See [here](https://docs.aws.amazon.com/lambda/latest/dg/urls-invocation.html) for more information on Lambda request/response payload structure.

The extractor will be automatically started when `docker-compose up -d --build` is run because eRegs depends on it.

No further action is required, but if you want the code to hot-reload during development, you may install `watchfiles` with `pip3 install watchfiles` and then run `make watch-text-extractor`.

# Request structure

The following data structure is required:

```jsonc
{
    "id": 1,                                 // The eRegs database ID of the object to update
    "uri": "object_uri",                     // The web URL or object name to extract text from
    "post_url": "https://api-url-here/",     // The API URL to POST the text to
    "token": "xxxxxx",                       //  If the return point uses a jwt token for authentication
    "backend": "s3",                         // Optional - defaults to 'web'
    // Only include if using the S3 backend
    "aws": {
        "aws_access_key_id": "xxxxxx",       // The access key for the AWS bucket
        "aws_secret_access_key": "xxxxxx",   // The AWS secret key
        "aws_storage_bucket_name": "xxxxxx",  // The name of the bucket to retrieve the object from
        "use_lambda": true,                  //  If you are using a local text extractor or a deployed text extractor(pertains to local development)
        "aws_region": "us-east-1"            // AWS region for Textract
    },
}
```

It is recommended to run this asynchronously as it could take time to run, up to several minutes for large PDF files, for example. If you are running this through API Gateway, set the POST body to a stringified version of the structure above.

If you wish to directly invoke this function, you may do so like this:

```python
import boto3
import json

request = {
    # ...the structure from above goes here...
}

data = json.dumps(request).encode()  # JSONify the request and convert it to bytes

client = boto3.client("lambda")      # Include access keys/region here if needed
response = client.invoke(
    FunctionName="lambda-arn-here",
    InvocationType="Event",          # Include this if you want to run the lambda async, as recommended
    Payload=data,                    # You may include raw JSON here
)
```

Direct invocation is the easiest way to asynchronously run the text extractor. Otherwise, it will be required to set up a proxy Lambda function that accepts the POST request from API Gateway and asynchronously invokes this one.

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
from .sample import SampleBackend as SampleBackend  # Note the redundant alias, a recommended way of avoiding linting errors
.... etc ...
```

The backend is now registered and will be automatically instantiated when `"backend": "sample"` is included in the POST request.

# Creating a new text extractor

To add support for a new file type (or group of file types), create a new file in the `extractors` directory and create a class inheriting from the `Extractor` class. Then add the new extractor class to `__init__.py` to register it, like so:

_`extractors/sample.py`_:
```python
from .extractor import Extractor

class SampleExtractor(Extractor):
    file_types = ("filetype1", "filetype2", ...)

    def extract(self, file: bytes) -> str:
        return ...extract text here...
```

_`extractors/__init__.py`_:
```python
.... etc ....

# Add your file extractors here to initialize them
.... etc ....
from .sample import SampleExtractor as SampleExtractor  # Note the redundant alias, a recommended way of avoiding linting errors
.... etc ....
```

The extractor is now registered and will be automatically instantiated when a file has one of the MIME types listed in `file_types`.

## Extracting embedded files

Many types of files contain other files within them. For example, an email has attachments. You can use the `_extract_embedded` method of the `Extractor` class to do so. For example:

```python
class SampleExtractor(Extractor):
    file_types = ("filetype1", "filetype2", ...)

    def extract(self, file: bytes) -> str:
        text = get_the_text(file)
        attachments = get_the_attachments(file)
        for i in attachments:
            file_name = i.name
            file_data = i.data
            text += self._extract_embedded(file_name, file_data)
```

In this example, lines 5 and 6 are pseudocode and we suppose that an Attachment object contains 2 attributes: `name` representing the file name with a valid extension, and `data` containing a byte array of the file's contents. Customize to your unique needs. File name is _not_ important and can be made up as long as the extension is valid.

## Writing the file to disk

When writing an extractor, it is sometimes necessary to save the file's byte array to a temporary file on disk. This could be because the file is too large, or possibly because a library you're using only accepts files from disk and not byte arrays. In either case, you can easily do this with the `_write_file` method of the `Extractor` class, like so:

```python
class SampleExtractor(Extractor):
    file_types = ("filetype1", "filetype2", ...)

    def extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        return extract_text_by_path(file_path)
```

This method returns a path to a temporary file stored on disk. You may access it using standard Python techniques.

## Unit testing your new extractor

In most cases, testing an extractor is done by providing one or more sample (fixture) files, and a text file containing expected output. I recommend at least one fixture showing a successful output. In some cases, you may wish to use additional (variation) files to capture edge cases. A test case like this can be accomplished by extending the `FixtureTestCase` class, like so:

_`extractors/tests/test_sample.py`_:
```python
from . import FixtureTestCase


class TestSampleExtractor(FixtureTestCase):
    def test_extract(self):
        # Save your fixture as "extractors/tests/fixtures/filetype1/sample.filetype1"
        # Save your expected output as "extractors/tests/fixtures/filetype1/expected.txt"
        self._test_file_type("filetype1")

    def test_extract_corrupt_variation(self):
        # Save your fixture as "extractors/tests/fixtures/filetype1/corrupt_sample.filetype1"
        # Save your expected output as "extractors/tests/fixtures/filetype1/corrupt_expected.txt"
        self._test_file_type("filetype1", variation="corrupt")

    def test_extract_with_config(self):
        self._test_file_type("filetype1", config={"some": "config"})
```

## Generating new fixture files

You can also easily use the existing unit test suite to generate new fixture files, instead of doing it manually. Just edit the file `extractors/tests/__init__.py` and uncomment the 2 lines near the bottom of the file, below the comment that says `Uncomment these 2 lines to re-export fixture files the next time tests are run.`.

Be sure to re-comment these 2 lines when you're done, or fixture files will be re-created every time you run unit tests, which may produce undesired behavior.
