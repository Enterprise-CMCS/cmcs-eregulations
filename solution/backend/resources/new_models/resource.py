from django.db import models

from model_utils.managers import InheritanceManager

from common.fields import (
    NaturalSortField,
    StatuteRefField,
    UscRefField,
    VariableDateField,
)
from common.mixins import DisplayNameFieldMixin

from . import NewAbstractCategory, AbstractCitation, NewSubject


class NewAbstractResource(models.Model, DisplayNameFieldMixin):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=True)
    category = models.ForeignKey(
        NewAbstractCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="resources"
    )
    citations = models.ManyToManyField(AbstractCitation, blank=True, related_name="resources")
    citation_history = models.JSONField(default=list)
    subjects = models.ManyToManyField(NewSubject, blank=True, related_name="resources")

    statute_citations = StatuteRefField(verbose_name="Statute reference citations")
    usc_citations = UscRefField(verbose_name="U.S.C. reference citations")

    internal_notes = models.TextField(blank=True)
    name = models.CharField(max_length=512, blank=True)
    description = models.TextField(blank=True)
    date = VariableDateField(blank=True)

    url = models.URLField(max_length=512, blank=True)
    extract_url = models.URLField(max_length=512, blank=True)

    name_sort = NaturalSortField("name", null=True)
    description_sort = NaturalSortField("description", null=True)

    objects = InheritanceManager()


class PublicResource(NewAbstractResource):
    pass


class InternalResource(NewAbstractResource):
    pass
