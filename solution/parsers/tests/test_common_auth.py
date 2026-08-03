import unittest
from unittest.mock import patch

from common.auth import resolve_backend_credentials
from common.config import ConfigParseError
from common.auth import BackendCredentials


class CommonAuthTests(unittest.TestCase):
    def test_resolve_from_message_credentials(self):
        creds = resolve_backend_credentials(
            {
                "auth_type": "basic",
                "username": "queue-user",
                "password": "queue-pass",
            }
        )

        self.assertEqual(creds.auth_type, "basic")
        self.assertEqual(creds.username, "queue-user")
        self.assertEqual(creds.password, "queue-pass")

    def test_fallback_to_env_when_message_credentials_blank(self):
        with patch.dict(
            "os.environ",
            {
                "EREGS_USERNAME": "env-user",
                "EREGS_PASSWORD": "env-pass",
            },
            clear=True,
        ):
            creds = resolve_backend_credentials(
                {
                    "auth_type": "basic",
                    "username": "",
                    "password": "",
                }
            )

        self.assertEqual(creds.auth_type, "basic")
        self.assertEqual(creds.username, "env-user")
        self.assertEqual(creds.password, "env-pass")

    def test_resolve_from_env_without_message_credentials(self):
        with patch.dict(
            "os.environ",
            {
                "EREGS_USERNAME": "env-user",
                "EREGS_PASSWORD": "env-pass",
            },
            clear=True,
        ):
            creds = resolve_backend_credentials(None)

        self.assertEqual(creds.auth_type, "basic")
        self.assertEqual(creds.username, "env-user")
        self.assertEqual(creds.password, "env-pass")

    def test_resolve_from_secret_when_configured(self):
        with patch.dict("os.environ", {"EREGS_AUTH_SECRET_NAME": "my/secret"}, clear=True):
            with patch("common.auth._load_credentials_from_secret") as load_secret:
                load_secret.return_value = BackendCredentials(
                    auth_type="basic",
                    username="secret-user",
                    password="secret-pass",
                )
                creds = resolve_backend_credentials(None)

        load_secret.assert_called_once_with("my/secret")
        self.assertEqual(creds.auth_type, "basic")
        self.assertEqual(creds.username, "secret-user")
        self.assertEqual(creds.password, "secret-pass")

    def test_raises_when_no_credentials_configured(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ConfigParseError, "Backend credentials are not configured"):
                resolve_backend_credentials(None)


if __name__ == "__main__":
    unittest.main()
