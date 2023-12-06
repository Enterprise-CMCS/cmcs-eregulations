from django.contrib.auth.models import Group, User
from django.test import TestCase, Client
from django.urls import reverse
import random
import string

class PolicyRepositoryViewTest(TestCase):

    def setUp(self):
        # Create a test user and assign it to a group
        self.password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.user = User.objects.create_user(username='testuser', password=self.password)
        self.reader_group = Group.objects.create(name='EREGS_READER')
        self.admin_group = Group.objects.create(name='EREGS_ADMIN')
        self.manager_group = Group.objects.create(name='EREGS_MANAGER')
        self.user.groups.add(self.reader_group)
        self.client = Client()

    def test_has_editable_job_code_true(self):
        # Log in the user
        self.client.force_login(self.user)
        self.user.groups.add(self.admin_group)

        # Access the PolicyRepositoryView
        response = self.client.get(reverse('policy-repository'))

        # Check if has_editable_job_code is True
        self.assertTrue(response.context['has_editable_job_code'])

    def test_has_editable_job_code_True_when_user_in_manager_group(self):
        # Log in the user
        self.client.force_login(self.user)
        self.user.groups.add(self.manager_group)

        # Access the PolicyRepositoryView
        response = self.client.get(reverse('policy-repository'))

        # Check if has_editable_job_code is False
        self.assertTrue(response.context['has_editable_job_code'])

    def test_has_editable_job_code_true_when_user_in_reader_and_manager_group(self):
        # Log in the user
        self.client.force_login(self.user)
        self.user.groups.add(self.manager_group)
        self.user.groups.add(self.reader_group)

        # Access the PolicyRepositoryView
        response = self.client.get(reverse('policy-repository'))

        # Check if has_editable_job_code is False
        self.assertTrue(response.context['has_editable_job_code'])

    def test_has_editable_job_code_false_when_user_in_reader_group(self):
        # Log in the user
        self.client.force_login(self.user)

        # Access the PolicyRepositoryView
        response = self.client.get(reverse('policy-repository'))

        # Check if has_editable_job_code is False
        self.assertFalse(response.context['has_editable_job_code'])

    def test_has_editable_job_code_false_when_user_in_no_group(self):
        # Remove the user from the EREGS_READER group
        self.user.groups.remove(self.reader_group)

        # Log in the user
        self.client.force_login(self.user)

        # Access the PolicyRepositoryView
        response = self.client.get(reverse('policy-repository'))

        # Check if has_editable_job_code is False
        self.assertFalse(response.context['has_editable_job_code'])

    def test_has_editable_job_code_fale_when_user_in_unkown_new_group(self):
        # Create a new group
        self.new_group = Group.objects.create(name='NEW_GROUP')
        self.user.groups.add(self.new_group)

        # Log in the user
        self.client.force_login(self.user)

        # Access the PolicyRepositoryView
        response = self.client.get(reverse('policy-repository'))

        # Check if has_editable_job_code is False
        self.assertFalse(response.context['has_editable_job_code'])
