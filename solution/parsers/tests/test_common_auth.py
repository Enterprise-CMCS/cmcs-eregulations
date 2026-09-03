import base64
import unittest
from unittest.mock import patch

from common.config import ConfigParseError

from common.auth import BackendCredentials, build_auth_headers, resolve_backend_credentials


class CommonAuthTests(unittest.TestCase):
    def test_build_auth_headers_basic(self):
        headers = build_auth_headers(
            BackendCredentials(auth_type="basic", username="queue-user", password="queue-pass")
        )
        expected = "Basic " + base64.b64encode(b"queue-user:queue-pass").decode("utf-8")
        self.assertEqual(headers, {"Authorization": expected})

    def test_build_auth_headers_bearer(self):
        headers = build_auth_headers(BackendCredentials(auth_type="bearer", token="secret-token"))
        self.assertEqual(headers, {"Authorization": "Bearer secret-token"})

    def test_build_auth_headers_invalid(self):
        with self.assertRaisesRegex(ConfigParseError, "authorization headers"):
            build_auth_headers(BackendCredentials(auth_type="basic", username="", password=""))

    def test_resolve_from_env_when_credentials_present(self):
        with patch.dict(
            "os.environ",
            {
                "EREGS_USERNAME": "env-user",
                "EREGS_PASSWORD": "env-pass",
            },
            clear=True,
        ):
            creds = resolve_backend_credentials()

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
                creds = resolve_backend_credentials()

        load_secret.assert_called_once_with("my/secret")
        self.assertEqual(creds.auth_type, "basic")
        self.assertEqual(creds.username, "secret-user")
        self.assertEqual(creds.password, "secret-pass")

    def test_raises_when_no_credentials_configured(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ConfigParseError, "Backend credentials are not configured"):
                resolve_backend_credentials()


if __name__ == "__main__":
    unittest.main()
