from django.db import models
from django.db.models.expressions import RawSQL
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchHeadline,
    SearchVectorField,
)

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
        search_query = SearchQuery(query, search_type=search_type, config='english')

        return self.annotate(rank=SearchRank(
                RawSQL("vector_column", [], output_field=SearchVectorField()),
                search_query, cover_density=cover_density)
            )\
            .filter(rank__gte=0.2)\
            .annotate(
                headline=SearchHeadline(
                    "content",
                    search_query,
                    start_sel='<span class="search-highlight">',
                    stop_sel='</span>',
                    config='english'
                ),
                parentHeadline=SearchHeadline(
                    "section_title",
                    search_query,
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


class SearchIndexV2(models.Model):
    part_number = models.CharField(max_length=32)
    section_number = models.CharField(max_length=32)
    content = models.TextField()
    section_string = models.CharField(max_length=32)
    section_title = models.TextField(null=True)
    part_title = models.TextField(null=True)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    objects = SearchIndexManager()


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
    if piece.get("node_type", None) == "SECTION":
        si = SearchIndexV2(
            part_number=piece["label"][0],
            section_number=piece["label"][1],
            section_title=piece["title"],
            part_title=part.document['title'],
            part=part,
            section_string=piece["label"][0] + "." + piece["label"][1],
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
    SearchIndexV2.objects.filter(part=instance).delete()
    contexts = create_search(instance, instance.document, [])
    SearchIndexV2.objects.bulk_create(contexts, ignore_conflicts=True)
