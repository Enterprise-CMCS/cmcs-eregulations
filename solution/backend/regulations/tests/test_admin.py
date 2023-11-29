import unittest
from unittest.mock import patch

from django.contrib.auth.models import Group, User  # Import the Group model
from django.test import TransactionTestCase

from ..admin import OidcAdminAuthenticationBackend


class OidcAdminAuthenticationBackendTest(TransactionTestCase):
    def setUp(self):
        self.backend = OidcAdminAuthenticationBackend()
        self.mock_claims = {
            "sub": "00u1234567891234297",
            "name": "Homer Simpson",
            "lastName": "Simpson",
            "firstName": "Homer",
            "email": "homer.simpson@example.com",
            "email_verified": True,
            "jobcodes": "cn=EREGS_ADMIN,cn=EREGS_EDITOR, ou=Groups,dc=cms,dc=hhs,dc=gov,cn=EXAMPLE_TEST,ou=Groups,"
                        "dc=cms,dc=hhs,dc=gov "
        }

    @patch.object(OidcAdminAuthenticationBackend, 'create_user')
    def test_verify_claims(self, mock_create_user):
        result = self.backend.verify_claims(self.mock_claims)
        self.assertTrue(result)

        invalid_claims = dict(self.mock_claims)
        invalid_claims["email_verified"] = False
        result = self.backend.verify_claims(invalid_claims)
        self.assertFalse(result)

    @patch.object(OidcAdminAuthenticationBackend, 'create_user')
    def test_user_is_active_if_have_jobcodes(self, mock_create_user):
        # Create a user with valid jobcodes
        user = User(email='homer.simpson@example.com')
        mock_create_user.return_value = user
        user = self.backend.create_user(self.mock_claims)

        # Assert that the user is active
        self.assertTrue(user.is_active)

    def test_user_without_jobcodes_return_none(self):
        self.mock_claims["jobcodes"] = ""
        user = self.backend.create_user(self.mock_claims)
        assert user is None

    def test_update_user(self):
        self.user = User.objects.create(username='test_user', email='test@example.com')

        # Create real Group instances
        group_admin = Group.objects.create(name='EREGS_ADMIN')
        group_editor = Group.objects.create(name='EREGS_EDITOR')
        # Create a list of groups to add to the user
        groups_to_add = [group_admin, group_editor]

        with unittest.mock.patch.object(Group.objects, 'filter', return_value=groups_to_add):
            updated_user = self.backend.update_user(self.user, self.mock_claims)

        # Ensure the user is updated
        self.assertEqual(updated_user.first_name, 'Homer')
        self.assertEqual(updated_user.last_name, 'Simpson')
        self.assertTrue(updated_user.is_active)

        # Ensure the user is associated with the correct groups
        self.assertTrue(updated_user.groups.filter(name='EREGS_ADMIN').exists())
        self.assertTrue(updated_user.groups.filter(name='EREGS_EDITOR').exists())

        # Ensure the user is not associated with the incorrect groups
        self.assertFalse(updated_user.groups.filter(name='EREGS_READER').exists())

    # Ensure user with EREGS_ADMIN jobcode is staff, active and superuser
    def test_user_with_admin_jobcode(self):
        self.mock_claims["jobcodes"] = "cn=EREGS_ADMIN,ou=Groups,dc=cms,dc=hhs,dc=gov"
        user = self.backend.create_user(self.mock_claims)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)

    # Ensure user with EREGS_EDITOR jobcode is staff, active and not superuser
    def test_user_with_editor_jobcode(self):
        self.mock_claims["jobcodes"] = "cn=EREGS_EDITOR,ou=Groups,dc=cms,dc=hhs,dc=gov"
        user = self.backend.create_user(self.mock_claims)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

    # Ensure user with EREGS_MANAGER jobcode is staff, active and not superuser
    def test_user_with_editor_jobcode(self):
        self.mock_claims["jobcodes"] = "cn=EREGS_MANAGER,ou=Groups,dc=cms,dc=hhs,dc=gov"
        user = self.backend.create_user(self.mock_claims)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

    # Ensure user with EREGS_READER jobcode is not staff, active and not superuser
    def test_user_with_reader_jobcode(self):
        self.mock_claims["jobcodes"] = "cn=EREGS_READER,ou=Groups,dc=cms,dc=hhs,dc=gov"
        user = self.backend.create_user(self.mock_claims)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

    # Ensure user with EREGS_READER_V jobcode is not staff, active and not superuser
    def test_user_with_reader_v_jobcode(self):
        self.mock_claims["jobcodes"] = "cn=EREGS_READER_V,ou=Groups,dc=cms,dc=hhs,dc=gov"
        user = self.backend.create_user(self.mock_claims)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

    # Ensure user with EREGS_READER_P jobcode is not staff, active and not superuser
    def test_user_with_reader_p_jobcode(self):
        self.mock_claims["jobcodes"] = "cn=EREGS_READER_P,ou=Groups,dc=cms,dc=hhs,dc=gov"
        user = self.backend.create_user(self.mock_claims)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

    # Ensure user with EREGS_ADMIN and EREGS_EDITOR jobcodes is staff, active and superuser
    def test_user_with_admin_and_editor_jobcodes(self):
        self.mock_claims["jobcodes"] = "cn=EREGS_ADMIN,cn=EREGS_EDITOR,ou=Groups,dc=cms,dc=hhs,dc=gov"
        user = self.backend.create_user(self.mock_claims)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)

    # Ensure user with jobcode EREGS_ADMIN_V is staff, active and superuser
    def test_user_with_admin_v_jobcode(self):
        self.mock_claims["jobcodes"] = "cn=EREGS_ADMIN_V,ou=Groups,dc=cms,dc=hhs,dc=gov"
        user = self.backend.create_user(self.mock_claims)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)

    # Ensure user with jobcode EREGS_ADMIN_P is staff, active and superuser
    def test_user_with_admin_p_jobcode(self):
        self.mock_claims["jobcodes"] = "cn=EREGS_ADMIN_P,ou=Groups,dc=cms,dc=hhs,dc=gov"
        user = self.backend.create_user(self.mock_claims)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)


if __name__ == '__main':
    unittest.main()
