# Contents

1. [About](#about)
2. [Supported file types](#supported-file-types)
3. [Running locally](#running-locally)
4. [Request structure](#request-structure)
    2. [Currently supported backends](#currently-supported-backends)
5. [Response structure](#response-structure)
6. [Creating a new file backend](#creating-a-new-file-backend)
7. [Creating a new text extractor](#creating-a-new-text-extractor)
    1. [Extracting embedded files](#extracting-embedded-files)
    2. [Writing the file to disk](#writing-the-file-to-disk)
    3. [Setting a file size limit for file extraction](#setting-a-file-size-limit-for-file-extraction)
    4. [Unit testing your new extractor](#unit-testing-your-new-extractor)
    5. [Storing fixture files in a "collection"](#storing-fixture-files-in-a-collection)
    6. [Generating new fixture files](#generating-new-fixture-files)
    7. [Determining file types and fixing misdetected ones](#determining-file-types-and-fixing-misdetected-ones)

# About

This Lambda function is run to extract text from a variety of file types and POST it to an arbitrary URL. The purpose of this is to support eRegs' full-text search goals as our users begin uploading files to the policy repository.

# Supported file types

The text extractor supports the following file types. File types that are planned but not yet implemented are not checked.

- [x] Plain text (txt, multiple encodings supported, currently excluding UTF-16)
- [x] HTML and XML (html, htm, xhtml, xml)
- [x] PDF
- [x] Images (png, jpeg, gif, tiff, bmp, tga, webp)
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
    "token": "xxxxxx",                       // If the return point uses a jwt token for authentication
    "backend": "s3",                         // Optional - defaults to 'web'
    "ignore_max_size": true,                 // Optional - include in request to ignore any size restrictions
    "ignore_robots_txt": true,               // Optional - include to ignore robots.txt
    // Only necessary to include if the POST endpoint uses authentication
    "auth": {
        // See below for configuring authentication
    },
    // Only necessary to include if using the S3 backend
    "aws": {
        "aws_access_key_id": "xxxxxx",       // The access key for the AWS bucket
        "aws_secret_access_key": "xxxxxx",   // The AWS secret key
        "aws_storage_bucket_name": "xxxxxx", // The name of the bucket to retrieve the object from
        "use_lambda": true,                  // If you are using a local text extractor or a deployed text extractor (pertains to local development)
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

## Configuring authentication

The text extractor supports the use of basic authentication and token authentication. For basic auth, configure your request like so:

```jsonc
"auth": {
    "type": "basic",
    "username": "xxxxxx",
    "password": "xxxxxx"
}
```

To use basic auth but retrieve the credentials from environment variables, configure like this:

```jsonc
"auth": {
    "type": "basic-env",
    "username": "USERNAME_ENV_VAR",
    "password": "PASSWORD_ENV_VAR"
}
```

To use token-based authentication, configure like this:

```jsonc
"auth": {
    "type": "token",
    "token": "xxxxxx"
}
```

## Currently supported backends

The text extractor currently supports downloading files from Amazon S3 (`s3`) and the web (`web`).

If you're using the S3 backend, you must include the `aws` dictionary in the example request above, with all listed keys specified. Then, set the `uri` to the key of the object stored in S3 that you wish to extract text from.

If you're using web, no further configuration is required. Set the `uri` to the URL to download, including the scheme (http or https). Note that the web backend has built-in retries in the event of a timeout or a `429 TOO MANY REQUESTS` response. By default, the extractor will wait 30 seconds between retries, or if a `Retry-After` header is specified, it will wait for the number of seconds specified there.

The extractor will continue retrying until the content downloads, a fatal error occurs, or the Lambda timeout occurs. Please note that if the Lambda timeout is increased, so too will the maximum amount of retries.

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

    def _extract(self, file: bytes) -> str:
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

The extractor is now registered and will be automatically instantiated when a file has one of the content types listed in `file_types`. See [Determining file types and fixing misdetected ones](#determining-file-types-and-fixing-misdetected-ones) for instructions on determine a file's content type.

Note the underscore in front of the `_extract()` method definition. Be sure to override this instead of `extract()` because the latter performs pre-extraction checks, then calls `_extract()`.

## Extracting embedded files

Many types of files contain other files within them. For example, an email has attachments. You can use the `_extract_embedded` method of the `Extractor` class to do so. For example:

```python
class SampleExtractor(Extractor):
    file_types = ("filetype1", "filetype2", ...)

    def _extract(self, file: bytes) -> str:
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

    def _extract(self, file: bytes) -> str:
        file_path = self._write_file(file)
        return extract_text_by_path(file_path)
```

This method returns a path to a temporary file stored on disk. You may access it using standard Python techniques.

## Setting a file size limit for file extraction

In some cases, it is necessary to limit the maximum file size that an extractor will attempt to process by default. This may be required for particularly slow extractors that are at risk of exceeding the 15 minute AWS Lambda timeout, or to reduce AWS costs associated with text extraction, among other possible reasons.

This behavior is built into the `Extractor` class but disabled by default. To enable it, set `max_size = N` in your custom extractor, like so:

```python
class SampleExtractor(Extractor):
    file_types = ("filetype1", "filetype2", ...)
    max_size = 5

    def _extract(self, file: bytes) -> str:
        ...
```

In this example, `max_size` is set to 5 megabytes. This means that if the file size is greater than 5MB, the extractor will raise an exception and refuse to process the file. To override the limit, include `ignore_max_size: true` in your JSON request to the Lambda.

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

## Storing fixture files in a "collection"

Most extractor unit tests will be one input, one output; that is, for every fixture file there is exactly one "expected.txt" file. However, in some cases there may be a group of files that have the same expected output text. For example, unit testing an external service that supports multiple file types. In this scenario, the API call to the external service must be mocked and so the true output cannot be used as "expected.txt", but instead "expected.txt" will contain some fake data to verify that the API call is working. You may handle cases like this like so:

_`extractors/tests/test_sample_collection.py`_:
```python
from unittest.mock import patch

from . import FixtureTestCase


def mock_external_api_extractor(file):
    if file.type not in ["filetype1", "filetype2", "filetype3"]:
        raise Exception("Invalid type")
    return "Fake data indicating the API call succeeded"


# For all of these tests, save your expected output as "extractors/tests/fixtures/group1/expected.txt"
class TestSampleExtractor(FixtureTestCase):
    @patch.object(some_module, "call_api_extractor", mock_external_api_extractor)
    def test_filetype1(self, *args):
        # Save your fixture as "extractors/tests/fixtures/group1/sample.filetype1"
        self._test_file_type("filetype1", collection="group1")

    @patch.object(some_module, "call_api_extractor", mock_external_api_extractor)
    def test_filetype2(self, *args):
        # Save your fixture as "extractors/tests/fixtures/group1/sample.filetype2"
        self._test_file_type("filetype2", collection="group1")

    @patch.object(some_module, "call_api_extractor", mock_external_api_extractor)
    def test_filetype3(self, *args):
        # Save your fixture as "extractors/tests/fixtures/group1/sample.filetype3"
        self._test_file_type("filetype3", collection="group1")
```

In this example, the "expected.txt" file should contain the text "Fake data indicating the API call succeeded" based on line 9.

Also note that this parameter can be used in conjunction with `variation`, and files are prefixed with the variation in the same way as shown in the previous section.

## Generating new fixture files

You can also easily use the existing unit test suite to generate new fixture files, instead of doing it manually. Just edit the file `extractors/tests/__init__.py` and uncomment the 2 lines near the bottom of the file, below the comment that says `Uncomment these 2 lines to re-export fixture files the next time tests are run.`.

Be sure to re-comment these 2 lines when you're done, or fixture files will be re-created every time you run unit tests, which may produce undesired behavior.

## Determining file types and fixing misdetected ones

The text extractor uses [Google's Magika library](https://github.com/google/magika) for content type detection, which uses a machine learning algorithm that promises greater than 99% accuracy when detecting known file types. However, not all file types are supported and their model has to be trained to support them.

You can [open an issue](https://github.com/google/magika/issues) on their repository to report a misdetection or missing file type. To do so, install Magika on your machine so that you can generate a report, like so:

```shell
$ pip install magika
$ magika --label --prediction-mode medium-confidence your-file.xyz
your-file.xyz: unknown
$ magika --generate-report your-file.xyz
your-file.xyz: Unknown binary data (unknown)
########################################
###              REPORT              ###
########################################
....... etc .......
```

Copy the `REPORT` section into the description of your GitHub issue to give the Magika team the information they need to fix the issue.
