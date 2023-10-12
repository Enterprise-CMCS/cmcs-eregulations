import unittest
from unittest.mock import patch, Mock
from django.contrib.auth import get_user_model
from ..admin import OidcAdminAuthenticationBackend

User = get_user_model()

class OidcAdminAuthenticationBackendTest(unittest.TestCase):
    def setUp(self):
        self.backend = OidcAdminAuthenticationBackend()
        self.mock_claims = {
            "sub": "00u1234567891234297",
            "name": "Homer Simpson",
            "lastName": "Simpson",
            "firstName": "Homer",
            "email": "homer.simpson@example.com",
            "email_verified": True,
            "jobcodes": "cn=EREGS_ADMIN,ou=Groups,dc=cms,dc=hhs,dc=gov,cn=EXAMPLE_TEST,ou=Groups,dc=cms,dc=hhs,dc=gov"
        }

    @patch.object(OidcAdminAuthenticationBackend, 'create_user', return_value=User(email='homer.simpson@example.com'))
    def test_verify_claims(self, mock_create_user):
        result = self.backend.verify_claims(self.mock_claims)
        self.assertTrue(result)

        invalid_claims = dict(self.mock_claims)
        invalid_claims["email_verified"] = False
        result = self.backend.verify_claims(invalid_claims)
        self.assertFalse(result)

    @patch.object(OidcAdminAuthenticationBackend, 'create_user')
    def test_user_is_active_if_have_jobcodes(self, mock_create_user):
        mock_create_user.return_value = User(email='homer.simpson@example.com')
        user = self.backend.create_user(self.mock_claims)
        self.assertTrue(user.is_active)

    def test_user_is_not_created_if_no_jobcodes(self):
        self.mock_claims["jobcodes"] = ''  # Simulate no jobcodes
        user = self.backend.create_user(self.mock_claims)
        self.assertIsNone(user)

if __name__ == '__main':
    unittest.main()
