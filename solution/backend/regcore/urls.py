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
)

from regcore.v3views import (
    ContentsViewSet,
    TitlesViewSet,
    TitleViewSet,
    TitleContentsViewSet,
    PartsViewSet,
    VersionsViewSet,
    PartContentsViewSet,
    PartSectionsViewSet,
    PartSubpartsViewSet,
    SubpartContentsViewSet,
    ParserResultViewSet,
    SynonymViewSet
)


router = DefaultRouter()
router.register("toc", ContentsViewSet)

urlpatterns = [
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
        path("toc", ContentsViewSet.as_view({
            "get": "list",
        })),
        path("titles", TitlesViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>", TitleViewSet.as_view({
            "get": "retrieve",
            "post": "create",
            "put": "update",
        })),
        path("title/<title>/toc", TitleContentsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/parts", PartsViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>/part/<part>/versions", VersionsViewSet.as_view({
            "get": "list",
        })),
        path("title/<title>/part/<part>/version/<version>/toc", PartContentsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/sections", PartSectionsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/subparts", PartSubpartsViewSet.as_view({
            "get": "retrieve",
        })),
        path("title/<title>/part/<part>/version/<version>/subpart/<subpart>/toc", SubpartContentsViewSet.as_view({
            "get": "retrieve",
        })),
        path("ecfr_parser_result/<title>", ParserResultViewSet.as_view({
            "get": "retrieve",
            "post": "create"
        })),
        path("synonym/<synonym>", SynonymViewSet.as_view({
            "get": "list"
        }) )
    ])),
]
