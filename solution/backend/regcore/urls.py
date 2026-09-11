from django.urls import include, path

from regcore.views import (
    contents,
    history,
    metadata,
    title,
)

urlpatterns = [
    path("v3/", include([
        path("resources/", include('resources.urls')),
        path("content-search/", include('content_search.urls')),
        path("parsers/", include('parsers.urls')),
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
        path("title/<title>/part/<part>/section/<section>/history", history.SectionHistoryViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>/part/<part>/section/<section>/versions", history.EcfrHistoryViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>/part/<part>", contents.PartViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/toc", metadata.PartTOCViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/sections", metadata.PartSectionsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/section/<section>", contents.SectionViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/subparts", metadata.PartSubpartsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/subpart/<subpart>", contents.SubpartViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/subpart/<subpart>/toc", metadata.SubpartTOCViewSet.as_view({
            "get": "retrieve",
        })),
    ])),
]
