import os
import uuid

from django.db import models

from .resources import AbstractInternalResource


class InternalLink(AbstractInternalResource):
    def __str__(self):
        return f"{self.document_id} {self.summary[:50]}"

    class Meta:
        verbose_name = "Internal Link"
        verbose_name_plural = "Internal Links"


class InternalFile(AbstractInternalResource):
    file_name = models.CharField(max_length=512, blank=True, editable=False)
    file_type = models.CharField(max_length=32, blank=True, editable=False)
    uid = models.UUIDField(
        primary_key=False,
        default=uuid.uuid4,
        editable=False,
    )

    @property
    def extension(self):
        return os.path.splitext(self.file_name)[1]

    @property
    def key(self):
        return f"uploaded_files/{str(self.uid)}{self.extension}" if self.file_name else ""

    def __str__(self):
        return f"{self.document_id} {self.summary[:50]}"

    class Meta:
        verbose_name = "Internal File"
        verbose_name_plural = "Internal Files"
