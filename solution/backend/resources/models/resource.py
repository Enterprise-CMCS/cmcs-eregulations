from django.db import models

from model_utils.managers import InheritanceManager

from common.fields import (
    NaturalSortField,
    StatuteRefField,
    UscRefField,
    VariableDateField,
)
from common.mixins import DisplayNameFieldMixin

from .category import NewAbstractCategory
from .citations import AbstractCitation
from .subject import NewSubject


class NewAbstractResource(models.Model, DisplayNameFieldMixin):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(
        default=True,
        help_text="Documents will be visible on eRegulations to all authorized users once they are approved.",
    )
    category = models.ForeignKey(
        NewAbstractCategory,
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
        help_text="Select regulation citations related to this document. "
                  "Hold down \"Control\", or \"Command\" on a Mac, to select more than one.",
    )
    cfr_citation_history = models.JSONField(default=list)

    subjects = models.ManyToManyField(
        NewSubject,
        blank=True,
        related_name="resources",
        help_text="Select subjects related to this document. Hold down \"Control\", or \"Command\" on a Mac, to select more than one.",
    )

    act_citations = StatuteRefField(verbose_name="Statute reference citations")
    usc_citations = UscRefField(verbose_name="U.S.C. reference citations")
    # TODO somehow add combined help text for these fields:
    # help_text="Designate statute citations that are related to this document."
    #           "You can use either the Act and Section of the Act, or the Title and Section of the U.S. Code."

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
    url = models.URLField(max_length=512, blank=True)
    extract_url = models.URLField(max_length=512, blank=True)

    document_id_sort = NaturalSortField("document_id", null=True)
    title_sort = NaturalSortField("title", null=True)

    objects = InheritanceManager()


class AbstractPublicResource(NewAbstractResource):
    pass


class AbstractInternalResource(NewAbstractResource):
    # TODO: add division foreignkey
    # help_text="Choose the Division that can see this document on eRegulations."
    #           "If it should be visible to everyone who is logged in, choose \"Visible to all CMCS\"."

    summary = models.TextField(
        blank=True,
        help_text="Write two or three sentences as a preview of the document for others.",
    )
