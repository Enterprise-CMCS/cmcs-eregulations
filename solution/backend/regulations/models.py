from django.db import models

from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    allow_indexing = models.BooleanField(default=False, help_text="Should robots be allowed to index this website?")

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"


class SSAToUSCConverter(models.Model):
    section = models.IntegerField()
    title = models.IntegerField()
    usc = models.CharField(max_length=128)

    def __str__(self):
        return f"Section {self.section} → {self.title} USC {self.usc}"

    class Meta:
        verbose_name = "SSA to USC Converter"
        verbose_name_plural = "SSA to USC Converters"
