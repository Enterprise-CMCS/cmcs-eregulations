#!/usr/bin/env python
import os
from django.contrib.auth.models import User


def handler(self, *args, **options):
    if not User.objects.filter(username='root').exists():
        User.objects.create_superuser('root', 'user@email.com', os.environ.get('DJANGO_ADMIN_PASSWORD', 'toor'))
