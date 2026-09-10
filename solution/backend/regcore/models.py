from django.db import models


class Part(models.Model):
    name = models.IntegerField()
    title = models.IntegerField()
    date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)

    document = models.JSONField()
    structure = models.JSONField()
    depth_stack = models.JSONField()
    depth = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("title", "name"),
                name="regcore_part_title_name_unique",
            ),
        ]
        ordering = ("title", "name")

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
