from django.core.validators import MinValueValidator
from django.db import models
from django_jsonform.models.fields import JSONField
from solo.models import SingletonModel

from resources.models import AbstractCategory


class ResourcesConfiguration(SingletonModel):
    fr_link_category = models.ForeignKey(
        AbstractCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="fr_link_category_config",
        help_text="The category that contains Federal Register Links. This affects all newly uploaded Federal Register Links.",
        verbose_name="FR Link Category",
    )

    state_medicaid_manual_category = models.ForeignKey(
        AbstractCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="smm_category_config",
        help_text="The category that contains State Medicaid Manual documents.",
        verbose_name="State Medicaid Manual Category",
    )

    auto_extract = models.BooleanField(
        default=False,
        help_text="Check this box if eRegs should automatically request text extraction on any resource when it is originally "
                  "saved/created or when its source is changed: URL (for public and internal links), document number "
                  "(for FR links), or attached file (for internal files).",
        verbose_name="Auto Extract",
    )

    extraction_delay_time = models.IntegerField(
        default=180,  # Default to 3 minutes
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="The number of seconds to delay between multiple text extraction requests. This is useful to prevent "
                  "overloading external services with too many requests in a short period of time.",
        verbose_name="Extraction Delay Time",
    )

    robots_txt_allow_list = JSONField(
        default=list,
        blank=True,
        help_text="A list of URLs and/or domains that the text extractor should be allowed to access, even if eRegs is not in "
                  "their robots.txt file. For example, 'example.com' will allow the entire domain and all subdomains to be "
                  "accessed, while 'https://example.com/page.html' will allow only that specific page.",
        verbose_name="Robots.txt Allow List",
        schema={
            "type": "list",
            "minItems": 0,
            "items": {
                "type": "string",
                "title": "URL or Domain",
                "placeholder": "example.com",
            },
        },
        pre_save_hook=lambda value: [url for url in [url.strip().lower() for url in value] if url],
    )

    user_agent_override_list = JSONField(
        default=list,
        blank=True,
        help_text="A list of domains and user agents that the text extractor should use instead of the default user agent. "
                  "This is useful for sites that block eRegs' default user agent. Note that a domain will match all subdomains.",
        verbose_name="User Agent Override List",
        schema={
            "type": "list",
            "minItems": 0,
            "items": {
                "type": "object",
                "title": "Domain and User Agent",
                "properties": {
                    "domain": {
                        "type": "string",
                        "title": "Domain",
                        "placeholder": "example.com",
                    },
                    "user_agent": {
                        "type": "string",
                        "title": "User Agent (optional)",
                        "placeholder": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
                    },
                },
                "required": ["domain"],
            },
        },
        pre_save_hook=lambda value: [
            {"domain": item["domain"].strip(), "user_agent": item.get("user_agent", "").strip()}
            for item in value if item.get("domain")
        ],
    )

    default_user_agent_override = models.CharField(
        max_length=255,
        blank=True,
        help_text="A default user agent to use for all requests to domains in the user agent override list that do not "
                  "specify a user agent. This is useful for sites that block eRegs' default user agent.",
        verbose_name="Default User Agent Override",
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    )

    def __str__(self):
        return "Resources Configuration"

    class Meta:
        verbose_name = "Resources Configuration"
