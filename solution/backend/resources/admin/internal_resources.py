from django.contrib import admin

from .resources import AbstractInternalResourceAdmin
from resources.models import (
    InternalLink,
    InternalFile,
)


@admin.register(InternalLink)
class InternalLinkAdmin(AbstractInternalResourceAdmin):
    pass


@admin.register(InternalFile)
class InternalFileAdmin(AbstractInternalResourceAdmin):
    pass
