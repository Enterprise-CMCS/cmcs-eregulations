from django.db import models
from django.utils import timezone
from solo.models import SingletonModel
from datetime import date  # Add this import statement



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

class PartialDateField(models.DateField):
    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        print(f"Value: {value}")
        if value and (value.month is None or value.year is None):
            print(f"within validate: {value}")
            raise ValidationError("Both year and month are required in the partial date.")

    def to_python(self, value):
        print(f"within to_python")
        if isinstance(value, PartialDate):
            return value
        return PartialDate.from_date(value)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value:
            return value.to_date()
        return None


class PartialDate:
    def __init__(self, year, month, day=None):
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_date(cls, date):
        if date is None:
            return None
        return cls(date.year, date.month, date.day)

    def to_date(self):
        if self.year is None or self.month is None:
            return None
        return date(self.year, self.month, self.day) if self.day else date(self.year, self.month)

    def __str__(self):
        if self.year is not None and self.month is not None:
            return f"{self.year}-{self.month:02d}"
        return ""

def validate_partial_date(value):
    if value and (value.month is None or value.year is None):
        raise ValidationError("Both year and month are required in the partial date.")


class SiteConfiguration(models.Model):
    allow_indexing = models.BooleanField(default=False, help_text="Should robots be allowed to index this website?")

    DATE_TYPE_CHOICES = (
        ('effective', 'Effective'),
        ('amended', 'Amended'),
    )

    date_type = models.CharField(max_length=10, choices=DATE_TYPE_CHOICES)
    date = PartialDateField(null=True, blank=True)

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
