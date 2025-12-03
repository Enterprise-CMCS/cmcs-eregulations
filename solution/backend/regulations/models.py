from django.db import models
from solo.models import SingletonModel

from common.fields import (
    CfrRefField,
    NaturalSortField,
    StatuteRefField,
    UscRefField,
    VariableDateField,
)

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

    show_flash_banner = models.BooleanField(
        default=False,
        help_text="Should a flash banner be displayed at the top of every page?",
    )
    flash_banner_text = models.TextField(blank=True, help_text="The text to display in the flash banner.")

    default_title = models.IntegerField(
        default=42,
        help_text="The default title to use for dropdowns, selects, and tabs throughout the site.",
    )

    DATE_TYPE_CHOICES = (
        ('effective', 'Effective'),
        ('amended', 'Amended'),
    )

    date_fields = [
        {
            'name': 'us_code_house_gov',
            'verbose_name': 'US Code House.gov',
        },
        {
            'name': 'ssa_gov_compilation',
            'verbose_name': 'SSA.gov Compilation',
        },
        {
            'name': 'statute_compilation',
            'verbose_name': 'Statute Compilation',
        },
        {
            'name': 'us_code_annual',
            'verbose_name': 'US Code Annual',
        },
    ]

    for field in date_fields:
        field_name = field['name']
        field_verbose_name = field['verbose_name']

        locals()[f"{field_name}_date_type"] = models.CharField(
            max_length=10,
            choices=DATE_TYPE_CHOICES,
            default='',
            blank=True,
            null=True,
            verbose_name=f"{field_verbose_name} Date Type"
        )

        locals()[f"{field_name}_date"] = VariableDateField(
            verbose_name=f"{field_verbose_name} Date"
        )

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"


class StatuteLinkConfiguration(SingletonModel):
    link_statute_refs = models.BooleanField(
        default=True,
        help_text="Should eRegs link statutes of the form \"Section 1902 of the Act\" to house.gov?",
        verbose_name="Link Statute Refs",
    )

    link_usc_refs = models.BooleanField(
        default=True,
        help_text="Should eRegs link statutes of the form \"42 U.S.C. 123(a)\" to house.gov?",
        verbose_name="Link U.S.C. Refs",
    )

    statute_ref_exceptions = StatuteRefField(
        help_text="Statute references that are listed here will not be automatically linked.",
        verbose_name="Statute Ref Exceptions",
    )

    usc_ref_exceptions = UscRefField(
        help_text="U.S.C. references that are listed here will not be automatically linked.",
        verbose_name="U.S.C. Ref Exceptions",
    )

    @property
    def statute_ref_exceptions_dict(self):
        out = {}
        for i in self.statute_ref_exceptions:
            out.setdefault(i["act"], []).append(i["section"])
        return out

    @property
    def usc_ref_exceptions_dict(self):
        out = {}
        for i in self.usc_ref_exceptions:
            out.setdefault(i["title"], []).append(i["section"])
        return out

    def __str__(self):
        return "Statute Link Configuration"

    class Meta:
        verbose_name = "Statute Link Configuration"


class StatuteLinkConverter(models.Model):
    section = models.CharField(max_length=128, verbose_name="Act Section")
    title = models.IntegerField(verbose_name="USC Title")
    usc = models.CharField(max_length=128, verbose_name="USC Section")
    act = models.CharField(max_length=128, verbose_name="Act Name")
    name = models.CharField(max_length=512, verbose_name="Section Name")
    statute_title = models.IntegerField(verbose_name="Statute Title", null=True)
    source_url = models.CharField(max_length=512, blank=True, null=True, verbose_name="Source URL")

    section_sort = NaturalSortField("section", null=True)
    usc_sort = NaturalSortField("usc", null=True)

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


class RegulationLinkConfiguration(SingletonModel):
    link_to_ecfr = models.BooleanField(
        default=True,
        help_text="If a regulation does not exist in eRegs, should links redirect to eCFR?",
        verbose_name="Link to eCFR",
    )

    link_cfr_refs = models.BooleanField(
        default=True,
        help_text="Should eRegs link references of the form \"42 CFR part 123\"?",
        verbose_name="Link CFR Refs",
    )

    cfr_ref_exceptions = CfrRefField(
        help_text="CFR-type references that are listed here will not be automatically linked.",
        verbose_name="CFR Ref Exceptions",
    )

    @property
    def cfr_ref_exceptions_dict(self):
        out = {}
        for i in self.cfr_ref_exceptions:
            out.setdefault(i["title"], []).append(i["reference"])
        return out

    def __str__(self):
        return "Regulation Link Configuration"

    class Meta:
        verbose_name = "Regulation Link Configuration"
