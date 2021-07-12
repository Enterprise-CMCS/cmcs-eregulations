from django.db import models


class PartQuerySet(models.QuerySet):
    def effective(self, date):
        return self.filter(date__lte=date).order_by("name", "-date").distinct("name")


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
