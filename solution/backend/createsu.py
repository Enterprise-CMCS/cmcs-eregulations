#!/usr/bin/env python
import os

from secret_manager import get_password, get_username


def handler(self, *args, **options):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    import django
    django.setup()

    django_admin_username = get_username("DJANGO_SECRET", environment_fallback="DJANGO_ADMIN_USERNAME")
    django_admin_password = get_password("DJANGO_SECRET", environment_fallback="DJANGO_ADMIN_PASSWORD")
    django_username = get_username("READER_SECRET", environment_fallback="DJANGO_USERNAME")
    django_password = get_password("READER_SECRET", environment_fallback="DJANGO_PASSWORD")

    from django.contrib.auth.models import Group, User

    e_regs_admin_group, _ = Group.objects.get_or_create(name='EREGS_ADMIN')
    e_regs_reader_group, _ = Group.objects.get_or_create(name='EREGS_READER')
    # TBD - will be used in the future
    # e_regs_editor_group, _ = Group.objects.get_or_create(name='EREGS_EDITOR')
    # e_regs_manager_group, _ = Group.objects.get_or_create(name='EREGS_MANAGER')

    if not User.objects.filter(username=django_admin_username).exists():
        admin_user = User.objects.create_superuser(django_admin_username,
                                                   'admin_user@email.com',
                                                   django_admin_password)
    else:
        admin_user = User.objects.get(username=django_admin_username)

    if not User.objects.filter(username=django_username).exists():
        user = User.objects.create_superuser(django_username,
                                             'user@email.com',
                                             django_password)
    else:
        user = User.objects.get(username=django_username)

    admin_user.groups.set([e_regs_admin_group])
    user.groups.set([e_regs_reader_group])
