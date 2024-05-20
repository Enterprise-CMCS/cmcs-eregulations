import pytest

from user.models import Profile


@pytest.mark.django_db
def test_user_profile_creation(create_user, capsys):
    user = create_user

    # Capture the output to check signal
    captured = capsys.readouterr()
    print(captured.out)

    # Check if the profile is created
    assert Profile.objects.filter(user=user).exists()

    # Check the department field
    profile = Profile.objects.get(user=user)
    assert profile.department == ''


@pytest.mark.django_db
def test_user_profile_update(create_user, capsys):
    user = create_user

    # Capture the output to check signal
    captured = capsys.readouterr()
    print(captured.out)

    profile = Profile.objects.get(user=user)

    # Update the department field
    profile.department = '/DHHS/CMS/OA/CMCS/FMG/DFOE/FOEBB'
    profile.save()

    # Fetch the profile again and check the department field
    profile = Profile.objects.get(user=user)
    assert profile.department == '/DHHS/CMS/OA/CMCS/FMG/DFOE/FOEBB'
