from django.db import models

from django_jsonform.models.fields import ArrayField

from .resource import PublicResource


class FederalRegisterLink(PublicResource):
    docket_numbers = ArrayField(
        models.CharField(max_length=512, blank=True),
        default=list,
        blank=True,
    )
    document_number = models.CharField(max_length=255, blank=True, null=True)
    correction = models.BooleanField(default=False)
    withdrawal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date} {self.document_number}: {self.name}"
    
    class Meta:
        ordering = ["-date", "document_number", "name", "description"]
        verbose_name = "Federal Register Link"
        verbose_name_plural = "Federal Register Links"


class PublicLink(PublicResource):
    def __str__(self):
        return f"{self.date} {self.name} {self.description[:50]}"

    class Meta:
        ordering = ["-date", "name", "description"]
        verbose_name = "Public Link"
        verbose_name_plural = "Public Links"
