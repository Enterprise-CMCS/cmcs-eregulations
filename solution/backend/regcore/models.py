from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from solo.models import SingletonModel


class PartQuerySet(models.QuerySet):
    def effective(self, date):
        return self.filter(date__lte=date).order_by("name", "-date").distinct("name")

    def versions(self, title, part):
        return self.filter(name=part, title=title).order_by('-date').values("date")

    def titles_list(self):
        return self.order_by("title").distinct("title").values_list("title", flat=True)


class PartManager(models.Manager.from_queryset(PartQuerySet)):
    pass


class Part(models.Model):
    name = models.IntegerField()
    title = models.IntegerField()
    date = models.DateField()  # TODO: rename to version, more clarity
    last_updated = models.DateTimeField(auto_now=True)

    document = models.JSONField()
    structure = models.JSONField()
    depth_stack = models.JSONField()
    depth = models.IntegerField()

    objects = PartManager()

    class Meta:
        unique_together = ['name', 'title', 'date']
        ordering = ("title", "name", "-date")

    @property
    def toc(self):
        structure = self.structure
        for _ in range(self.depth):
            structure = structure["children"][0]
        return structure

    @property
    def subchapter(self):
        structure = self.structure
        for _ in range(self.depth - 1):
            structure = structure["children"][0]
        return structure["label"]


class ParserConfiguration(SingletonModel):
    LOGLEVEL_CHOICES = [
        ("fatal", "Fatal"),
        ("error", "Error"),
        ("warn", "Warning"),
        ("info", "Info"),
        ("debug", "Debug"),
        ("trace", "Trace"),
    ]

    workers = models.IntegerField(
        default=3,
        help_text="The number of worker threads used to parse simultaneously.",
        validators=[MinValueValidator(
            limit_value=1,
            message="Number of workers must be at least 1!",
        )],
    )
    retries = models.IntegerField(
        default=3,
        help_text="The number of times to retry parsing before moving on if it fails.",
        validators=[MinValueValidator(
            limit_value=0,
            message="The number of retries must be at least 0!",
        )],
    )
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
    log_parse_errors = models.BooleanField(
        default=False,
        help_text="Should the eCFR parser log errors encountered while processing the raw XML data from eCFR?",
    )
    skip_reg_versions = models.BooleanField(
        default=True,
        help_text="Should the eCFR parser skip processing versions of regulation parts that have been previously processed?",
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
        help_text="A subchapter or part to parse. E.g., \"IV-C\" or \"400\".",
        validators=[RegexValidator(
            regex="^([A-Za-z]+-[A-Za-z]+)|(\\d+)$",
            message="Please enter a valid part or subchapter, e.g. \"IV-C\" or \"400\".",
        )]
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
        return f'Title {self.title} {self.type} {self.value} config'

    class Meta:
        verbose_name = "Part"
        verbose_name_plural = "Parts"


class AbstractParserResult(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.IntegerField()
    subchapters = models.TextField(blank=True)
    parts = models.TextField(blank=True)
    workers = models.IntegerField()


class ECFRParserResult(AbstractParserResult):
    totalVersions = models.IntegerField()
    skippedVersions = models.IntegerField()
    errors = models.IntegerField()
