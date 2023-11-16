#!/usr/bin/env python
import os


def handler(self, *args, **options):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    import django
    django.setup()

    from django.contrib.auth.models import User

    if not User.objects.filter(username=os.environ.get('DJANGO_ADMIN_USERNAME')).exists():
        User.objects.create_superuser(os.environ.get('DJANGO_ADMIN_USERNAME'),
                                      'admin_user@email.com',
                                      os.environ.get('DJANGO_ADMIN_PASSWORD'))
    if not User.objects.filter(username=os.environ.get('DJANGO_USERNAME')).exists():
        User.objects.create_superuser(os.environ.get('DJANGO_USERNAME'),
                                      'user@email.com',
                                      os.environ.get('DJANGO_PASSWORD'))
