from django.contrib import admin
from solo.admin import SingletonModelAdmin

from common.admin import CustomAdminMixin
from content_search.models import ContentSearchConfiguration


@admin.register(ContentSearchConfiguration)
class ContentSearchConfigurationAdmin(CustomAdminMixin, SingletonModelAdmin):
    admin_priority = 0

    fieldsets = [
        ("Search Settings", {
            "fields": [
                "enable_keyword_search",
                "enable_semantic_search",
                "keyword_search_min_rank",
                "semantic_search_max_distance",
                "rrf_k_value",
            ],
        }),
        ("Extraction Settings", {
            "fields": [
                "auto_extract",
                "generate_embeddings",
                "extraction_delay_time",
            ]
        }),
        ("Crawling Settings", {
            "classes": ["collapse"],
            "fields": [
                "robots_txt_allow_list",
                "user_agent_override_list",
                "default_user_agent_override",
            ]
        }),
    ]
