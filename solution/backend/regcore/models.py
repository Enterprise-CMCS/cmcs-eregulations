from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

from solo.models import SingletonModel


class PartQuerySet(models.QuerySet):
    def effective(self, date):
        return self.filter(date__lte=date).order_by("name", "-date").distinct("name")

    def versions(self, title, part):
        return self.filter(name=part, title=title).order_by('-date').values("date")


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
        for _ in range(self.depth-1):
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


class TitleConfiguration(models.Model):
    title = models.IntegerField(unique=True, help_text="The title of the regulations to parse, e.g. 42.")
    subchapters = models.TextField(
        blank=True,
        help_text="A comma-separated list of subchapters to parse. All parts within the listed subchapters will be included. "
                  "E.g., \"IV-C, IV-D, IV-F\" or simply \"IV-C\".",
        validators=[RegexValidator(
            regex="^([A-Za-z]+-[A-Za-z]+)(,\\s*([A-Za-z]+-[A-Za-z]+))*$",
            message="Please enter a comma-separated list of subchapters, e.g. \"IV-C, IV-D, IV-F\" or \"IV-C\".",
        )]
    )
    parts = models.TextField(
        blank=True,
        help_text="A comma-separated list of individual parts to parse if you do not wish to include the entire subchapter. "
                  "E.g., \"400, 457, 460\" or simply \"400\".",
        validators=[RegexValidator(
            regex="^(\\d+)(,\\s*\\d+)*$",
            message="Please enter a comma-separated list of part numbers, e.g. \"400, 457, 460\" or \"400\".",
        )]
    )
    parser_config = models.ForeignKey(ParserConfiguration, on_delete=models.CASCADE, related_name="titles")

    def __str__(self):
        return f'Title {self.title} config'

    class Meta:
        verbose_name = "Title"
        verbose_name_plural = "Titles"


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
