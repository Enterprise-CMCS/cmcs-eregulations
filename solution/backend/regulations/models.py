from django.db import models

from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    allow_indexing = models.BooleanField(default=False, help_text="Should robots be allowed to index this website?")

    def __str__(self):
        return "Site Configuration"
    
    class Meta:
        verbose_name = "Site Configuration"
