#!/usr/bin/env python
import os


def handler(self, *args, **options):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    import django
    django.setup()

    from django.contrib.auth.models import User, Group

    e_regs_admin_group, _ = Group.objects.get_or_create(name='e-Regs-Admin')
    e_regs_reader_group, _ = Group.objects.get_or_create(name='e-Regs-Reader')

    if not User.objects.filter(username=os.environ.get('DJANGO_ADMIN_USERNAME')).exists():
        admin_user = User.objects.create_superuser(os.environ.get('DJANGO_ADMIN_USERNAME'),
                                      'admin_user@email.com',
                                      os.environ.get('DJANGO_ADMIN_PASSWORD'))
    else:
        admin_user = User.objects.get(username=os.environ.get('DJANGO_ADMIN_USERNAME'))

    if not User.objects.filter(username=os.environ.get('DJANGO_USERNAME')).exists():
        user = User.objects.create_superuser(os.environ.get('DJANGO_USERNAME'),
                                      'user@email.com',
                                      os.environ.get('DJANGO_PASSWORD'))
    else:
        user = User.objects.get(username=os.environ.get('DJANGO_USERNAME'))

    admin_user.groups.set([e_regs_admin_group])
    user.groups.set([e_regs_reader_group])
