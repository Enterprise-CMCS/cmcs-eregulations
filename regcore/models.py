from django.db import models

from solo.models import SingletonModel


class PartQuerySet(models.QuerySet):
    def effective(self, date):
        return self.filter(date__lte=date).order_by("name", "-date").distinct("name")

    def versions(self, title, part):
        return self.filter(name=part, title=title).order_by('-date').values("date")


class PartManager(models.Manager.from_queryset(PartQuerySet)):
    pass


class Part(models.Model):
    name = models.CharField(max_length=8)
    title = models.CharField(max_length=8)
    date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)
    document = models.JSONField()
    structure = models.JSONField()

    objects = PartManager()

    class Meta:
        unique_together = ['name', 'title', 'date']

    @property
    def toc(self):
        return self.structure['children'][0]['children'][0]['children'][0]


class ParserConfiguration(SingletonModel):
    LOGLEVEL_CHOICES = [
        ("warn", "Warning"),
        ("error", "Error"),
        ("fatal", "Fatal"),
        ("info", "Info"),
        ("debug", "Debug"),
        ("trace", "Trace"),
    ]

    workers = models.IntegerField(default=3, help_text="The number of worker threads used to parse regulations.")
    attempts = models.IntegerField(default=3, help_text="Number of times to retry parsing if it fails to complete.")
    loglevel = models.CharField(max_length=5, choices=LOGLEVEL_CHOICES, default="info", help_text="Specifies the level of detail contained in the parser's logs.")

    def __str__(self):
        return "Parser Configuration"
    
    class Meta:
        verbose_name = "Parser Configuration"


class TitleConfiguration(models.Model):
    title = models.IntegerField(unique=True, help_text="The title of the regulations to parse, e.g. 42.")
    subchapters = models.TextField(blank=True, help_text="A comma-separated list of subchapters to parse. All parts within the listed subchapters will be included. E.g., \"IV-C, IV-D, IV-F\" or simply \"IV-C\".")
    parts = models.TextField(blank=True, help_text="A comma-separated list of individual parts to parse if you do not wish to include the entire subchapter. E.g., \"400, 457, 460\".")
    parser_config = models.ForeignKey(ParserConfiguration, on_delete=models.CASCADE, related_name="titles")

    def __str__(self):
        return ""
