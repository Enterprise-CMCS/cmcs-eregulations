import os
import json

import boto3
from moto import mock_aws

from extractors import (
    Extractor,
)

from . import FixtureTestCase


class TestPdfExtractor(FixtureTestCase):
    CONFIG = {
        "id": 1234,
        "aws": {
            "aws_access_key_id": "xxxxxx",
            "aws_secret_access_key": "xxxxxx",
            "aws_region": "us-east-1",
        },
    }

    BUCKET_NAME = "test-bucket"
    QUEUE_NAME = "test-queue.fifo"

    def setUp(self):
        super().setUp()
        self.mock_aws = mock_aws()
        self.mock_aws.start()

        self.s3_client = boto3.client("s3", region_name=self.CONFIG["aws"]["aws_region"])
        self.s3_client.create_bucket(Bucket=self.BUCKET_NAME)

        self.sqs_client = boto3.client("sqs", region_name=self.CONFIG["aws"]["aws_region"])
        self.sqs_client.create_queue(
            QueueName=self.QUEUE_NAME,
            Attributes={
                "FifoQueue": "true",
                "ContentBasedDeduplication": "true",
            },
        )
        self.sqs_url = self.sqs_client.get_queue_url(QueueName=self.QUEUE_NAME)["QueueUrl"]

    def test_extract_pdf_async(self):
        # Start the async extraction
        os.environ["TEXTRACT_BUCKET"] = self.BUCKET_NAME
        os.environ["TEXT_EXTRACTOR_QUEUE_URL"] = self.sqs_url
        extractor = Extractor.get_extractor("pdf", self.CONFIG)
        output = extractor.extract(b"123")
        self.assertEqual(output, None)

        # After extract() returns, the PDF should be uploaded to S3
        objects = self.s3_client.list_objects_v2(Bucket=self.BUCKET_NAME)["Contents"]
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0]["Key"], f"{self.CONFIG['id']}.pdf")

        # After extract() returns, a new message with a job ID should be sent to the SQS queue
        messages = self.sqs_client.receive_message(
            QueueUrl=self.sqs_url,
            MaxNumberOfMessages=10,
        )["Messages"]
        self.assertEqual(len(messages), 1)
        body = json.loads(messages[0]["Body"])
        self.assertIn("job_id", body)
        self.assertEqual(body.get("id"), self.CONFIG["id"])

        # Simulate a continuation of the extraction process
        config = {**self.CONFIG, "job_id": extractor.config["job_id"]}
        extractor = Extractor.get_extractor("pdf", config)
        output = extractor.extract(None)
        self.assertEqual(output, "")  # moto returns a blank string for Textract results

        # Check that the S3 object was deleted after extraction
        s3_response = self.s3_client.list_objects_v2(Bucket=self.BUCKET_NAME)
        self.assertEqual(s3_response["KeyCount"], 0)

        # Check the SQS queue is empty
        sqs_response = self.sqs_client.receive_message(
            QueueUrl=self.sqs_url,
            MaxNumberOfMessages=10,
        )
        self.assertNotIn("Messages", sqs_response)  # No messages should be left

    def test_extract_pdf_sync(self):
        # Start the sync extraction
        os.environ["TEXTRACT_BUCKET"] = self.BUCKET_NAME
        os.environ["TEXT_EXTRACTOR_QUEUE_URL"] = ""
        extractor = Extractor.get_extractor("pdf", self.CONFIG)
        output = extractor.extract(b"123")
        self.assertEqual(output, "")  # moto returns a blank string for Textract results

        # Assert that the PDF is no longer in S3
        s3_response = self.s3_client.list_objects_v2(Bucket=self.BUCKET_NAME)
        self.assertEqual(s3_response["KeyCount"], 0)
