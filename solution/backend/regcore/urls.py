from django.urls import path, include

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
    title,
    part,
    contents,
    metadata,
    synonyms,
    parser,
    history,
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
        path("", include('regcore.search.v3urls')),
        path("toc", title.TOCViewSet.as_view({
            "get": "list",
        })),
        path("titles", title.TitlesViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>/toc", title.TitleTOCViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/parts", title.PartsViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>/versions", title.VersionsViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>/part/<part>/history/section/<section>", history.SectionHistoryViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>/part/<part>/versions", part.VersionsViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>/part/<part>/version/<version>", contents.PartViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/toc", metadata.PartTOCViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/sections", metadata.PartSectionsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/section/<section>", contents.SectionViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/subparts", metadata.PartSubpartsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/subpart/<subpart>", contents.SubpartViewSet.as_view({
            "get": "retrieve",
        })),
        path(
            "title/<title>/part/<part>/version/<version>/subpart/<subpart>/toc",
            metadata.SubpartTOCViewSet.as_view({
                "get": "retrieve",
            }),
        ),
        path("ecfr_parser_result/<title>", parser.ParserResultViewSet.as_view({
            "get": "retrieve",
            "post": "create",
        })),
        path("part", parser.PartUploadViewSet.as_view({
            "put": "update",
        })),
        path("synonym/<path:synonym>", synonyms.SynonymViewSet.as_view({
            "get": "list",
        })),
        path("parser_config", parser.ParserConfigurationViewSet.as_view({
            "get": "retrieve",
        })),
    ])),
]
