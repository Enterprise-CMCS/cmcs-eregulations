import os
import uuid

from django.db import models

from .resource import AbstractInternalResource


class InternalLink(AbstractInternalResource):
    pass


# Override the URL field's help_text for internal links specifically
InternalLink._meta.get_field("url").help_text = \
    "To link to an existing document - for example in Box or SharePoint - enter the full URL here."


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
        return f"uploaded_files/{str(self.uid)}{self.extension}"

    def __str__(self):
        return f"{self.document_id} {self.summary[:50]}"