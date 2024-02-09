#!/usr/bin/env python
import os


def handler(self, *args, **options):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmcs_regulations.settings.deploy")
    import django
    django.setup()

    from django.contrib.auth.models import Group, User

    e_regs_admin_group, _ = Group.objects.get_or_create(name='EREGS_ADMIN')
    e_regs_reader_group, _ = Group.objects.get_or_create(name='EREGS_READER')
    # TBD - will be used in the future
    # e_regs_editor_group, _ = Group.objects.get_or_create(name='EREGS_EDITOR')
    # e_regs_manager_group, _ = Group.objects.get_or_create(name='EREGS_MANAGER')

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
