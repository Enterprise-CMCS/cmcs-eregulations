import json
import unittest
from unittest.mock import Mock
from unittest.mock import patch

import boto3
from moto import mock_aws

from common.launcher import (
    build_launcher_response,
    is_local_mode,
    send_work_units,
    send_work_units_via_http,
)


class CommonLauncherTests(unittest.TestCase):
    def test_is_local_mode(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(is_local_mode())

        with patch.dict("os.environ", {"PARSER_LOCAL_MODE": "true"}, clear=True):
            self.assertTrue(is_local_mode())

    @mock_aws
    def test_send_work_units(self):
        sqs = boto3.client("sqs", region_name="us-east-1")
        queue_url = sqs.create_queue(QueueName="parser-test-queue")["QueueUrl"]
        work_units = [{"config": {"title_number": 42}}]

        send_work_units(queue_url, work_units)

        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
        messages = response.get("Messages", [])
        self.assertEqual(len(messages), 1)
        self.assertIn('"title_number": 42', messages[0]["Body"])

    def test_build_launcher_response(self):
        work_units = [{"config": {"document_number": "2026-12345"}}]
        response = build_launcher_response(
            work_units=work_units,
            local_mode=True,
            succeeded=1,
            failures=[],
        )

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")

        payload = json.loads(response["body"])
        self.assertEqual(payload["enqueued"], 1)
        self.assertTrue(payload["local_mode"])
        self.assertEqual(payload["succeeded"], 1)
        self.assertEqual(payload["failed"], 0)
        self.assertEqual(payload["failures"], [])
        self.assertEqual(payload["work_units"], work_units)

    @patch("common.launcher._http_post")
    def test_send_work_units_via_http_success(self, mock_http_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_http_post.return_value = mock_response

        work_units = [{"config": {"title_number": 42}}]
        success, failures = send_work_units_via_http("http://example.local", work_units)

        self.assertEqual(success, 1)
        self.assertEqual(failures, [])

    @patch("common.launcher._http_post")
    def test_send_work_units_via_http_failure(self, mock_http_post):
        mock_http_post.side_effect = RuntimeError("timed out")

        work_units = [{"config": {"title_number": 42}}]
        success, failures = send_work_units_via_http("http://example.local", work_units)

        self.assertEqual(success, 0)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["index"], "0")
        self.assertIn("timed out", failures[0]["reason"])


if __name__ == "__main__":
    unittest.main()
