from django.db import models
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

    auto_extract = models.BooleanField(
        default=False,
        help_text="Check this box if eRegs should automatically request text extraction on any resource when its URL or "
                  "attached file has changed.",
        verbose_name="Auto Extract",
    )

    def __str__(self):
        return "Resources Configuration"

    class Meta:
        verbose_name = "Resources Configuration"
