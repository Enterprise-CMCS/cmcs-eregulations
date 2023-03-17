from django.db import models

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    SearchHeadline,
)
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from datetime import datetime
from regcore.models import Part


class SearchIndexQuerySet(models.QuerySet):
    def effective(self, date):
        return self.filter(part__in=models.Subquery(Part.objects.effective(date.today()).values("id")))

    def search(self, query):
        search_type = "plain"
        cover_density = False
        if query and query.startswith('"') and query.endswith('"'):
            search_type = "phrase"
            cover_density = True
        sq = SearchQuery(query, search_type=search_type, config='english')
        return self\
            .annotate(rank=SearchRank(
                SearchVector('label', weight='A', config='english')
                + SearchVector(models.functions.Concat('label__0', models.Value('.'), 'label__1'), weight='A', config='english')
                + SearchVector('parent__title', weight='A', config='english')
                + SearchVector('part__document__title', weight='B', config='english'),
                sq, cover_density=cover_density)
            )\
            .filter(vector_column=query)\
            .filter(rank__gte=0.2)\
            .annotate(
                headline=SearchHeadline(
                    "content",
                    sq,
                    start_sel='<span class="search-highlight">',
                    stop_sel='</span>',
                    config='english'
                ),
                parentHeadline=SearchHeadline(
                    "parent__title",
                    sq,
                    start_sel="<span class='search-highlight'>",
                    stop_sel="</span>",
                    config='english',
                    highlight_all=True
                ),
            )\
            .order_by('-rank')\
            .prefetch_related('part')


class SearchIndexManager(models.Manager.from_queryset(SearchIndexQuerySet)):
    pass


class SearchIndex(models.Model):
    type = models.CharField(max_length=32)
    label = ArrayField(base_field=models.CharField(max_length=32))
    content = models.TextField()
    parent = models.JSONField(null=True)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    vector_column = SearchVectorField(null=True)
    objects = SearchIndexManager()

    class Meta:
        indexes = (GinIndex(fields=["vector_column"]),) # add index
        unique_together = ['label', 'part']


class Synonym(models.Model):
    isActive = models.BooleanField(default=True)
    baseWord = models.CharField(max_length=128)
    synonyms = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.baseWord if self.isActive else f'{self.baseWord} (inactive)'

    @property
    def filtered_synonyms(self):
        return self.synonyms.filter(isActive=True).order_by("baseWord")


def create_search(part, piece, memo, parent=None, ):
    print('creaste')
    if piece.get("node_type", None) == "SECTION":
        si = SearchIndex(
            label=piece["label"],
            part=part,
            parent=piece,
            type=piece["node_type"],
            content=piece.get("title", piece.get("text", "")),
        )
        children = piece.pop("children", []) or []
        for child in children:
            si.content = si.content + child.get("text", "")
        memo.append(si)
    else:
        children = piece.pop("children", []) or []
        for child in children:
            create_search(part, child, memo, parent=piece)

    return memo


def update_search(sender, instance, created, **kwargs):
    print('update')
    SearchIndex.objects.filter(part=instance).delete()
    contexts = create_search(instance, instance.document, [])
    SearchIndex.objects.bulk_create(contexts, ignore_conflicts=True)
