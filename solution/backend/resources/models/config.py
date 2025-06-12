from django.db import models
from solo.models import SingletonModel
from django_jsonform.models.fields import JSONField

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

    auto_extract = models.BooleanField(
        default=False,
        help_text="Check this box if eRegs should automatically request text extraction on any resource when it is originally "
                  "saved/created or when its source is changed: URL (for public and internal links), document number "
                  "(for FR links), or attached file (for internal files).",
        verbose_name="Auto Extract",
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
                "title": "URL",
                "placeholder": "https://www.example.com/*",
            },
        },
        pre_save_hook=lambda value: [url for url in [url.strip().lower() for url in value] if url],
    )

    def __str__(self):
        return "Resources Configuration"

    class Meta:
        verbose_name = "Resources Configuration"
