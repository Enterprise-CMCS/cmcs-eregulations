from django.db import models
from solo.models import SingletonModel

from resources.models import NewAbstractCategory


class NewResourcesConfiguration(SingletonModel):
    fr_link_category = models.ForeignKey(
        NewAbstractCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="fr_link_category_config",
        help_text="The category that contains Federal Register Links. This affects all newly uploaded Federal Register Links.",
    )

    def __str__(self):
        return "Resources Configuration"

    class Meta:
        verbose_name = "Resources Configuration"
