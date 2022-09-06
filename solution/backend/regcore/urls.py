from django.urls import path, include
from rest_framework.routers import DefaultRouter

from regcore.views import (
    EffectivePartView,
    EffectiveTitlesView,
    EffectivePartsView,
    EffectivePartTocView,
    PartsView,
    ExistingPartsView,
    ParserConfigurationView,
    PartListView,
    BulkSynonymView
)

from regcore.v3views import (
    synonyms_views,
    parser_views,
    title_views,
    part_views,
    version_contents_views,
    version_metadata_views,
)


urlpatterns = [
    path("admin/bulk_synonyms", BulkSynonymView.as_view(), name="bulk_synonyms"),
    path("v2/", include([
        path("", include('regcore.search.urls')),
        path("", include('resources.urls')),
        path("", PartsView.as_view(), name="regcore"),
        path("parser_config", ParserConfigurationView.as_view()),
        path("all_parts", PartListView.as_view()),
        path("title/<title>/part/<name>", PartsView.as_view()),
        path("<date>", EffectiveTitlesView.as_view()),
        path("<date>/title/<title>", EffectivePartsView.as_view()),
        path("<date>/title/<title>/part/<name>", EffectivePartView.as_view()),
        path("<date>/title/<title>/part/<name>/toc", EffectivePartTocView.as_view()),
        path("title/<title>/existing", ExistingPartsView.as_view()),
    ])),
    path("v3/", include([
        path("resources/", include('resources.v3urls')),
        path("toc", title_views.ContentsViewSet.as_view({
            "get": "list",
        })),
        path("titles", title_views.TitlesViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>", title_views.TitleViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/toc", title_views.TitleContentsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/parts", title_views.PartsViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>/part/<part>/versions", part_views.VersionsViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>/part/<part>/version/<version>", version_contents_views.PartViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/toc", version_metadata_views.PartContentsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/sections", version_metadata_views.PartSectionsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/section/<section>", version_contents_views.SectionViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/subparts", version_metadata_views.PartSubpartsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/subpart/<subpart>", version_contents_views.SubpartViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/subpart/<subpart>/toc", version_metadata_views.SubpartContentsViewSet.as_view({
            "get": "retrieve",
        })),
        path("ecfr_parser_result/<title>", parser_views.ParserResultViewSet.as_view({
            "get": "retrieve",
            "post": "create"
        })),
        path("synonym/<synonym>", synonyms_views.SynonymViewSet.as_view({
            "get": "list"
        }))
    ])),
]
