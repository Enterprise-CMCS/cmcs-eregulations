import secrets
import string

import pytest
from django.contrib.auth.models import User


@pytest.fixture
def create_user():
    password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    user = User.objects.create_user(username='testuser', password=password, email='testuser@example.com')
    return user
