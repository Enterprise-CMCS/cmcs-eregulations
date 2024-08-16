from django.contrib import admin
from solo.admin import SingletonModelAdmin

from common.admin import CustomAdminMixin
from resources.models import (
    AbstractPublicCategory,
    ResourcesConfiguration,
)


@admin.register(ResourcesConfiguration)
class ResourcesConfigurationAdmin(CustomAdminMixin, SingletonModelAdmin):
    admin_priority = 0

    foreignkey_lookups = {
        "fr_link_category": lambda: AbstractPublicCategory.objects.select_subclasses(),
    }
