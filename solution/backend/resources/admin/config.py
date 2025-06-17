from django.contrib import admin
from solo.admin import SingletonModelAdmin

from common.admin import CustomAdminMixin
from resources.models import (
    AbstractInternalCategory,
    AbstractPublicCategory,
    ResourcesConfiguration,
)


@admin.register(ResourcesConfiguration)
class ResourcesConfigurationAdmin(CustomAdminMixin, SingletonModelAdmin):
    admin_priority = 0

    fields = ["fr_link_category", "state_medicaid_manual_category", "robots_txt_allow_list", "auto_extract"]

    foreignkey_lookups = {
        "fr_link_category": lambda: AbstractPublicCategory.objects.select_subclasses(),
        "state_medicaid_manual_category": lambda: AbstractInternalCategory.objects.select_subclasses(),
    }
