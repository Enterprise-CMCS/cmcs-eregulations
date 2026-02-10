from django.db import models
from django_jsonform.models.fields import ArrayField

from .resources import AbstractPublicResource

FR_ACTION_TYPES = [("Notice", "Notice"), ("RFI", "RFI"), ("NPRM", "NPRM"), ("Final", "Final")]


class FederalRegisterLink(AbstractPublicResource):
    docket_numbers = ArrayField(
        models.CharField(max_length=512, blank=True),
        default=list,
        blank=True,
    )
    document_number = models.CharField(
        max_length=255,
        blank=True,
        help_text="This is a unique number for the rule that usually looks like "
                  "\"90-6614\" and is listed at the very end of the rule.",
    )

    correction = models.BooleanField(default=False)
    withdrawal = models.BooleanField(default=False)
    # TODO: find a way to include this help text below both fields
    # help_text="If this document is a correction or withdrawal of another document, "
    #           "marking that action will change its display within eRegulations."

    action_type = models.CharField(
        blank=True,
        max_length=32,
        choices=FR_ACTION_TYPES,
        default="",
    )

    def __str__(self):
        return f"{self.date} {self.document_number}: {self.document_id}"

    class Meta:
        ordering = ["-date", "document_number", "document_id", "title"]
        verbose_name = "Federal Register Link"
        verbose_name_plural = "Federal Register Links"


class PublicLink(AbstractPublicResource):
    def __str__(self):
        return f"{self.date} {self.document_id} {self.title[:50]}"

    class Meta:
        ordering = ["-date", "document_id", "title"]
        verbose_name = "Public Link"
        verbose_name_plural = "Public Links"
