#!/usr/bin/env python
import os
from django.contrib.auth.models import User


def handler(self, *args, **options):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings")
    if not User.objects.filter(username=os.environ.get('DJANGO_ADMIN_USERNAME')).exists():
        User.objects.create_superuser(os.environ.get('DJANGO_ADMIN_USERNAME'),
                                      'user@email.com',
                                      os.environ.get('DJANGO_ADMIN_PASSWORD'))
