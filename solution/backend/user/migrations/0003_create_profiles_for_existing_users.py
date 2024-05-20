# Generated by Django 5.0.6 on 2024-05-23 14:42

from django.db import migrations

def create_profiles_for_existing_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('user', 'Profile')
    existing_users = User.objects.all()

    for user in existing_users:
        Profile.objects.get_or_create(user=user)

class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_profile_department'),  # Adjust the dependency to your last migration file
    ]

    operations = [
        migrations.RunPython(create_profiles_for_existing_users),
    ]