from django.db import models


class SingleStringModel(models.Model):
    value = models.TextField(blank=True)

    def __str__(self):
        return self.value
