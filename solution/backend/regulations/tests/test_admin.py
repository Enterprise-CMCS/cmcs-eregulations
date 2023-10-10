import unittest

from ..admin import OidcAdminAuthenticationBackend


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

    def test_verify_claims(self):
        result = self.backend.verify_claims(self.mock_claims)
        self.assertTrue(result)

        invalid_claims = dict(self.mock_claims)
        invalid_claims["email_verified"] = False
        result = self.backend.verify_claims(invalid_claims)
        self.assertFalse(result)

    def test_create_user(self):
        user = self.backend.create_user(self.mock_claims)
        self.assertEqual(user.email, "homer.simpson@example.com")
        self.assertEqual(user.username, "homer.simpson@example.com")
        self.assertEqual(user.first_name, "Homer")
        self.assertEqual(user.last_name, "Simpson")

    def update_user_if_changed(self):
        self.backend.create_user(self.mock_claims)
        self.mock_claims["email"] = "homerjsimpson@example.com"
        user = self.backend.create_user(self.mock_claims)
        self.assertEqual(user.email, "homerjsimpson@example.com")

    def test_user_is_active_if_have_jobcodes(self):
        user = self.backend.create_user(self.mock_claims)
        self.assertTrue(user.is_active)

    def test_user_is_not_active_if_no_jobcodes(self):
        self.mock_claims["jobcodes"] = ''
        user = self.backend.create_user(self.mock_claims)
        self.assertFalse(user.is_active)

if __name__ == '__main__':
    unittest.main()
