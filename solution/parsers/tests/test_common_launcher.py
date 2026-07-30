import unittest
from unittest.mock import patch

import boto3
from moto import mock_aws

from common.launcher import (
    build_basic_credentials_from_env,
    build_launcher_response,
    is_local_mode,
    send_work_units,
)


class CommonLauncherTests(unittest.TestCase):
    def test_is_local_mode(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(is_local_mode())

        with patch.dict("os.environ", {"PARSER_LOCAL_MODE": "true"}, clear=True):
            self.assertTrue(is_local_mode())

    def test_build_basic_credentials_from_env(self):
        with patch.dict(
            "os.environ",
            {"EREGS_USERNAME": "local-user", "EREGS_PASSWORD": "local-pass"},
            clear=True,
        ):
            creds = build_basic_credentials_from_env()
            self.assertEqual(
                creds,
                {
                    "auth_type": "basic",
                    "username": "local-user",
                    "password": "local-pass",
                },
            )

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
        response = build_launcher_response(work_units, local_mode=True)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["enqueued"], 1)
        self.assertTrue(response["local_mode"])
        self.assertEqual(response["work_units"], work_units)


if __name__ == "__main__":
    unittest.main()
