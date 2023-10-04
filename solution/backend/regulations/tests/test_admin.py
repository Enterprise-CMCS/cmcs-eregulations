from ..admin import OidcAdminAuthenticationBackend
import unittest

class OidcAdminAuthenticationBackendTest(unittest.TestCase):
    def setUp(self):
        self.backend = OidcAdminAuthenticationBackend()
        self.mock_claims = {
          "sub": "00u1234567891234297",
          "name": "Homer Simpson",
          "email": "homer.simpson@example.com",
          "ver": 1,
          "iss": "https://test.idp.idm.cms.gov/oauth2/auski5g1bm92sixcI297",
          "aud": "0oaki5f4a8HEu2NqT297",
          "iat": 1691531583,
          "exp": 1691535183,
          "jti": "ID.fXnaIz7cYWataUnGdT9bTPAxlOWMzYgoWsTwGEg0UqI",
          "amr": [
            "pwd"
          ],
          "idp": "00o3te9s7wZfoqqxb296",
          "nonce": "nonce",
          "preferred_username": "HJSD",
          "auth_time": 1000,
          "at_hash": "preview_at_hash",
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
        self.assertEqual(user.username, "HJSD")
        self.assertEqual(user.first_name, "Homer")
        self.assertEqual(user.last_name, "Simpson")

    def test_is_staff_true_if_user_has_jobcodes(self):
      user = self.backend.create_user(self.mock_claims)
      self.assertTrue(user.is_staff)

    def test_is_staff_false_if_user_has_no_jobcodes(self):
      self.mock_claims["jobcodes"] = ''
      user = self.backend.create_user(self.mock_claims)
      self.assertFalse(user.is_staff)

if __name__ == '__main__':
    unittest.main()
