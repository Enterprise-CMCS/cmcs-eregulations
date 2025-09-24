from django.contrib import admin
from solo.admin import SingletonModelAdmin

from common.admin import CustomAdminMixin
from content_search.models import ContentSearchConfiguration


@admin.register(ContentSearchConfiguration)
class ContentSearchConfigurationAdmin(CustomAdminMixin, SingletonModelAdmin):
    admin_priority = 0

    fields = [
        "extraction_delay_time",
        "robots_txt_allow_list",
        "user_agent_override_list",
        "default_user_agent_override",
        "auto_extract",
    ]
