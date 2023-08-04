from django.urls import include, path

from regcore.admin import BulkSynonymView
from regcore.views import (
    contents,
    history,
    metadata,
    parser,
    part,
    synonyms,
    title,
)

urlpatterns = [
    path("admin/bulk_synonyms", BulkSynonymView.as_view(), name="bulk_synonyms"),
    path("v3/", include([
        path("resources/", include('resources.urls')),
        path("search/", include('regcore.search.urls')),
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
        path("synonyms", synonyms.SynonymViewSet.as_view({
            "get": "list",
        })),
        path("parser_config", parser.ParserConfigurationViewSet.as_view({
            "get": "retrieve",
        })),
    ])),
]
