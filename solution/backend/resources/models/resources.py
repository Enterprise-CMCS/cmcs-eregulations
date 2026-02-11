from django.core.exceptions import ValidationError
from django.db import models
from model_utils.managers import InheritanceManager

from common.fields import (
    VariableDateField,
)
from common.mixins import DisplayNameFieldMixin

from .categories import AbstractCategory
from .citations import AbstractCitation, ActCitation, UscCitation
from .subjects import Subject


class AbstractResource(models.Model, DisplayNameFieldMixin):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(
        default=True,
        help_text="Documents will be visible on eRegulations to all authorized users once they are approved.",
    )
    category = models.ForeignKey(
        AbstractCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resources",
        help_text="Choose a single category or subcategory for the document. "
                  "Choosing a subcategory will also apply the category when the document is listed.",
    )

    cfr_citations = models.ManyToManyField(
        AbstractCitation,
        blank=True,
        related_name="resources",
        verbose_name="CFR citations",
        help_text="Select regulation citations related to this document. "
                  "Hold down \"Control\", or \"Command\" on a Mac, to select more than one.",
    )

    act_citations = models.ManyToManyField(
        ActCitation,
        blank=True,
        related_name="resources",
        help_text="Select Act citations related to this document. "
                  "Hold down \"Control\", or \"Command\" on a Mac, to select more than one.",
    )

    usc_citations = models.ManyToManyField(
        UscCitation,
        blank=True,
        related_name="resources",
        verbose_name="USC citations",
        help_text="Select USC citations related to this document. "
                  "Hold down \"Control\", or \"Command\" on a Mac, to select more than one.",
    )

    subjects = models.ManyToManyField(
        Subject,
        blank=True,
        related_name="resources",
        help_text="Select subjects related to this document. Hold down \"Control\", "
                  "or \"Command\" on a Mac, to select more than one.",
    )

    editor_notes = models.TextField(
        blank=True,
        help_text="Use this field to store notes meant for other editors. "
                  "Notes in this field are not displayed outside this editing screen.",
    )

    document_id = models.CharField(
        max_length=512,
        blank=True,
        help_text="Some documents have an identifier, such as \"SMDL #04-002\" or \"State Medicaid Manual Section 4442.3\".",
        verbose_name="Document ID",
    )

    title = models.TextField(blank=True)
    date = VariableDateField(blank=True)
    url = models.URLField(max_length=512, blank=True, verbose_name="URL")
    extract_url = models.URLField(max_length=512, blank=True, verbose_name="Extract URL")

    file_type = models.CharField(
        max_length=32,
        blank=True,
        help_text="The file type of the document. Only use this field if the automatically detected file type is incorrect, "
                  "and the document content is not extracting correctly as a result.",
    )

    related_resources = models.ManyToManyField("self", blank=True, symmetrical=False)
    related_citations = models.ManyToManyField(AbstractCitation, blank=True)
    related_act_citations = models.ManyToManyField(ActCitation, blank=True)
    related_usc_citations = models.ManyToManyField(UscCitation, blank=True)
    related_categories = models.ManyToManyField(AbstractCategory, blank=True)
    related_subjects = models.ManyToManyField(Subject, blank=True)
    group_parent = models.BooleanField(default=True)

    objects = InheritanceManager()

    @property
    def indexing_status(self):
        try:
            index_metadata = getattr(self, "index_metadata")
            if not index_metadata:
                return "Not indexed"
            if index_metadata.extraction_error:
                return f"Error: {index_metadata.extraction_error}"
            indices = getattr(self, "indices")
            if not indices or not indices.exists():
                return "Not indexed"
            index = indices.first()
            return f"Indexed: {index.content[:100]}..."
        except Exception as e:
            return str(e)

    @property
    def number_of_chunks(self):
        indices = getattr(self, "indices")
        if not indices or not indices.exists():
            return 0
        return indices.count()

    @property
    def detected_file_type(self):
        index_metadata = getattr(self, "index_metadata")
        if index_metadata and index_metadata.detected_file_type:
            return index_metadata.detected_file_type
        return "Not detected"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class AbstractPublicResource(AbstractResource):
    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if self.url and AbstractPublicResource.objects.filter(url__iexact=self.url).exclude(pk=self.pk):
            raise ValidationError(f"A public resource with the URL \"{self.url}\" already exists.")


class AbstractInternalResource(AbstractResource):
    # TODO: add division foreignkey
    # help_text="Choose the Division that can see this document on eRegulations."
    #           "If it should be visible to everyone who is logged in, choose \"Visible to all CMCS\"."

    summary = models.TextField(
        blank=True,
        help_text="Write two or three sentences as a preview of the document for others.",
    )
