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

    fields = [
        "fr_link_category",
        "state_medicaid_manual_category",
        "extraction_delay_time",
        "robots_txt_allow_list",
        "user_agent_override_list",
        "default_user_agent_override",
        "auto_extract",
    ]

    foreignkey_lookups = {
        "fr_link_category": lambda: AbstractPublicCategory.objects.select_subclasses(),
        "state_medicaid_manual_category": lambda: AbstractInternalCategory.objects.select_subclasses(),
    }
