from django.db import models

from common.fields import CombinedNaturalSort
from common.mixins import DisplayNameFieldMixin


class Subject(models.Model, DisplayNameFieldMixin):
    full_name = models.CharField(max_length=512, blank=False)
    short_name = models.CharField(max_length=50, blank=True)
    abbreviation = models.CharField(max_length=10, blank=True)
    description = models.TextField(blank=True)

    combined_sort = CombinedNaturalSort(['short_name', 'abbreviation', 'full_name'], null=True)

    def __str__(self):
        short_name = f" {self.short_name} " if self.short_name else ""
        abbreviation = f" ({self.abbreviation})" if self.abbreviation else ""
        return f"{self.full_name}{short_name}{abbreviation}"

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
