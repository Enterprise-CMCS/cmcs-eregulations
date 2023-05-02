from django.db import models

from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    allow_indexing = models.BooleanField(default=False, help_text="Should robots be allowed to index this website?")

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"


class StatuteLinkConverter(models.Model):
    section = models.CharField(max_length=128, verbose_name="Act Section")
    title = models.IntegerField(verbose_name="USC Title")
    usc = models.CharField(max_length=128, verbose_name="USC Section")
    act = models.CharField(max_length=128, verbose_name="Act Name")
    source_url = models.CharField(max_length=512, blank=True, null=True, verbose_name="Source URL")

    def __str__(self):
        return f"Title {self.title} section {self.section} → {self.title} USC {self.usc}"

    class Meta:
        verbose_name = "Statute Link Converter"
        verbose_name_plural = "Statute Link Converters"
