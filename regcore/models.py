from django.db import models


class PartQuerySet(models.QuerySet):
    def effective(self, date):
        return self.filter(date__lte=date).order_by("name", "-date").distinct("name")

    def effective_title(self, date, title):
        return self.filter(title=title).filter(date__lte=date).order_by("name", "-date").distinct("name")

    def full_part(self, date, title, part):
        return self.filter(title=title).filter(date__lte=date).filter(name=part).latest("date")

    def versions(self, title, part):
        return self.filter(name=part).filter(title=title).order_by('-date')


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
