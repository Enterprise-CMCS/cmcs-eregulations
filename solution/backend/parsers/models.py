from django.core.validators import RegexValidator
from django.db import models
from solo.models import SingletonModel


class ParserConfiguration(SingletonModel):
    LOGLEVEL_CHOICES = [
        ("fatal", "Fatal"),
        ("error", "Error"),
        ("warn", "Warning"),
        ("info", "Info"),
        ("debug", "Debug"),
        ("trace", "Trace"),
    ]

    loglevel = models.CharField(
        max_length=5,
        choices=LOGLEVEL_CHOICES,
        default="warn",
        help_text="Specifies the level of detail contained in the parser's logs.",
    )
    upload_supplemental_locations = models.BooleanField(
        default=True,
        help_text="Should the eCFR parser process and upload section and subpart names for use in resource management?",
    )
    skip_parsed_regs = models.BooleanField(
        default=True,
        help_text="Should the eCFR parser skip processing regulation parts that have been previously processed?",
    )
    skip_fr_documents = models.BooleanField(
        default=True,
        help_text="Should the Federal Register parser skip processing documents that have been previously processed?",
    )

    def __str__(self):
        return "Parser Configuration"

    class Meta:
        verbose_name = "Parser Configuration"


class PartConfiguration(models.Model):
    TYPES = [
        ("subchapter", "Subchapter"),
        ("part", "Part"),
    ]

    title = models.IntegerField(help_text="The title of the regulations to parse, e.g. 42.")
    type = models.CharField(max_length=255, choices=TYPES, default="part")
    value = models.CharField(
        max_length=255,
        help_text='A subchapter or part to parse. E.g., "IV-C" or "400".',
        validators=[
            RegexValidator(
                regex="^([A-Za-z]+-[A-Za-z]+)|(\\d+)$",
                message='Please enter a valid part or subchapter, e.g. "IV-C" or "400".',
            )
        ],
    )
    upload_reg_text = models.BooleanField(
        default=True,
        help_text="Should the eCFR parser upload regulation text to eRegs?",
    )
    upload_locations = models.BooleanField(
        default=True,
        help_text="Should the parser process and upload section and subpart names for use in resource management?",
    )
    upload_fr_docs = models.BooleanField(
        default=True,
        help_text="Should the FR parser upload Federal Register Documents to eRegs?",
    )

    parser_config = models.ForeignKey(ParserConfiguration, on_delete=models.CASCADE, related_name="parts")

    def __str__(self):
        return f"Title {self.title} {self.type} {self.value} config"

    class Meta:
        verbose_name = "Part"
        verbose_name_plural = "Parts"


class AbstractParserResult(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    log = models.TextField()


class EcfrParserResult(AbstractParserResult):
    STATUS_QUEUED = "queued"
    STATUS_SKIPPED = "skipped"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_QUEUED, "Queued"),
        (STATUS_SKIPPED, "Skipped"),
        (STATUS_SUCCEEDED, "Succeeded"),
        (STATUS_FAILED, "Failed"),
    ]

    launcher_result = models.ForeignKey(
        "EcfrLauncherResult",
        on_delete=models.CASCADE,
        related_name="part_results",
        null=True,
        blank=True,
    )
    title = models.IntegerField()
    part = models.IntegerField()
    date = models.DateField(null=True, blank=True)  # this is the date the part was released, not the date the parser ran
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_SUCCEEDED)
    status_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "eCFR Parser Result"
        verbose_name_plural = "eCFR Parser Results"
        indexes = [
            models.Index(fields=["title", "part"]),
            models.Index(fields=["title"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["launcher_result", "title", "part", "date"],
                name="unique_ecfr_part_result_per_launcher_run",
            )
        ]


class EcfrLauncherResult(AbstractParserResult):
    class Meta:
        verbose_name = "eCFR Launcher Result"
        verbose_name_plural = "eCFR Launcher Results"


class FrParserResult(AbstractParserResult):
    document_number = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Federal Register Parser Result"
        verbose_name_plural = "Federal Register Parser Results"
        indexes = [
            models.Index(fields=["document_number"]),
        ]


class FrLauncherResult(AbstractParserResult):
    queued_count = models.PositiveIntegerField(default=0)
    skipped_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Federal Register Launcher Result"
        verbose_name_plural = "Federal Register Launcher Results"
