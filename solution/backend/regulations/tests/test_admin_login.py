import json
import os
from unittest.mock import patch

import boto3
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from moto import mock_aws

from regulations.admin_login import clear_admin_login_cache


@mock_aws
@override_settings(
    ADMIN_LOGIN_LOCAL_OVERRIDE=None,
    ADMIN_LOGIN_ENABLED_PARAMETER="/eregulations/admin-login-enabled",
    ADMIN_LOGIN_CYPRESS_TOKEN_SECRET="/eregulations/admin-login-cypress-token",  # noqa: S106
)
class AdminLoginViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.environment = patch.dict(
            os.environ,
            {
                "AWS_ACCESS_KEY_ID": "testing",
                "AWS_DEFAULT_REGION": "us-east-1",
                "AWS_SECRET_ACCESS_KEY": "testing",
            },
            clear=False,
        )
        self.environment.start()
        self.ssm = boto3.client("ssm", region_name="us-east-1")
        self.secrets_manager = boto3.client("secretsmanager", region_name="us-east-1")
        self.ssm.put_parameter(
            Name="/eregulations/admin-login-enabled",
            Value="false",
            Type="String",
        )
        self.secrets_manager.create_secret(
            Name="/eregulations/admin-login-cypress-token",
            SecretString=json.dumps({"token": "cypress-test-token"}),
        )
        clear_admin_login_cache()

    def tearDown(self):
        clear_admin_login_cache()
        self.environment.stop()
        super().tearDown()

    def test_admin_login_is_not_found_when_disabled(self):
        response = self.client.get("/admin/login/")

        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, 'id="id_username"', status_code=404)
        self.assertIn("no-store", response["Cache-Control"])

    def test_admin_login_allows_manual_outage_flag(self):
        self.ssm.put_parameter(
            Name="/eregulations/admin-login-enabled",
            Value="true",
            Type="String",
            Overwrite=True,
        )
        clear_admin_login_cache()

        response = self.client.get("/admin/login/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="id_username"')

    def test_admin_login_allows_valid_cypress_token(self):
        response = self.client.get(
            "/admin/login/",
            HTTP_X_EREGS_CYPRESS_ADMIN_TOKEN="cypress-test-token",  # noqa: S106
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="id_username"')

        response = self.client.post("/admin/login/")

        self.assertEqual(response.status_code, 200)

    def test_admin_login_rejects_invalid_cypress_token(self):
        response = self.client.get(
            "/admin/login/",
            HTTP_X_EREGS_CYPRESS_ADMIN_TOKEN="incorrect-token",  # noqa: S106
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_login_fails_closed_when_aws_configuration_is_missing(self):
        self.ssm.delete_parameter(Name="/eregulations/admin-login-enabled")
        self.secrets_manager.delete_secret(
            SecretId="/eregulations/admin-login-cypress-token",
            ForceDeleteWithoutRecovery=True,
        )
        clear_admin_login_cache()

        response = self.client.get(
            "/admin/login/",
            HTTP_X_EREGS_CYPRESS_ADMIN_TOKEN="cypress-test-token",  # noqa: S106
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_login_authenticates_staff_user_when_enabled(self):
        User.objects.create_user(username="admin", password="admin-password", is_staff=True)  # noqa: S106
        self.ssm.put_parameter(
            Name="/eregulations/admin-login-enabled",
            Value="true",
            Type="String",
            Overwrite=True,
        )
        clear_admin_login_cache()

        response = self.client.post(
            "/admin/login/",
            {"username": "admin", "password": "admin-password", "next": "/admin/"},
        )

        self.assertRedirects(response, "/admin/", fetch_redirect_response=False)

    def test_custom_oidc_login_remains_available(self):
        response = self.client.get("/login/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Continue to CMS IDM")
