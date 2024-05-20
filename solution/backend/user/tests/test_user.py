import pytest
from django.contrib.auth.models import User

from user.models import Profile


@pytest.mark.django_db
def test_user_profile_creation():
    # Create a user
    user = User.objects.create_user(username='testuser', password='password123', email='testuser@example.com')

    # Check if the profile is created
    assert Profile.objects.filter(user=user).exists()

    # Check the department field
    profile = Profile.objects.get(user=user)
    assert profile.department == ''


@pytest.mark.django_db
def test_user_profile_update():
    # Create a user
    user = User.objects.create_user(username='testuser', password='password123', email='testuser@example.com')
    profile = Profile.objects.get(user=user)

    # Update the department field
    profile.department = '/DHHS/CMS/OA/CMCS/DEHPG'
    profile.save()

    # Fetch the profile again and check the department field
    profile = Profile.objects.get(user=user)
    assert profile.department == '/DHHS/CMS/OA/CMCS/DEHPG'
