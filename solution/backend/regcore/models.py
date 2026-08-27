from django.db import models


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
