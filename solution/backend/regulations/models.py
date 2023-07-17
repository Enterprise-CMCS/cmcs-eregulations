from django.db import models
from common.fields import VariableDateField
from django.core.exceptions import ValidationError
from solo.models import SingletonModel


ROMAN_TABLE = [
    [1000, "M"],
    [900, "CM"],
    [500, "D"],
    [400, "CD"],
    [100, "C"],
    [90, "XC"],
    [50, "L"],
    [40, "XL"],
    [10, "X"],
    [9, "IX"],
    [5, "V"],
    [4, "IV"],
    [1, "I"]
]


class SiteConfiguration(SingletonModel):

    allow_indexing = models.BooleanField(default=False, help_text="Should robots be allowed to index this website?")

    DATE_TYPE_CHOICES = (
        ('effective', 'Effective'),
        ('amended', 'Amended'),
    )

    date_type = models.CharField(
        max_length=10,
        choices=DATE_TYPE_CHOICES,
        default='',
        blank=True,
        null=True
    )
    date = VariableDateField()

    def __str__(self):
        return f"{self.get_date_type_display()} {self.get_formatted_date()}"

    def get_formatted_date(self):
        if self.date:
            return str(self.date)
        return ""

    class Meta:
        verbose_name = "Site Configuration"


class StatuteLinkConverter(models.Model):
    section = models.CharField(max_length=128, verbose_name="Act Section")
    title = models.IntegerField(verbose_name="USC Title")
    usc = models.CharField(max_length=128, verbose_name="USC Section")
    act = models.CharField(max_length=128, verbose_name="Act Name")
    name = models.CharField(max_length=512, verbose_name="Section Name")
    statute_title = models.IntegerField(verbose_name="Statute Title", null=True)
    source_url = models.CharField(max_length=512, blank=True, null=True, verbose_name="Source URL")

    @property
    def statute_title_roman(self):
        num = self.statute_title
        if not num:
            return None
        roman = ""
        for i in range(len(ROMAN_TABLE)):
            while num >= ROMAN_TABLE[i][0]:
                roman += ROMAN_TABLE[i][1]
                num -= ROMAN_TABLE[i][0]
        return roman

    def __str__(self):
        return f"Title {self.title} section {self.section} → {self.title} USC {self.usc}"

    class Meta:
        verbose_name = "Statute Link Converter"
        verbose_name_plural = "Statute Link Converters"
