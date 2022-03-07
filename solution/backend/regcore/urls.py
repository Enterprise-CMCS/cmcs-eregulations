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
)


router = DefaultRouter()
router.register("toc", ContentsViewSet)

urlpatterns = [
    path("v2/", include([
        path("", include('regcore.search.urls')),
        path("", include('supplemental_content.urls')),
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
        path("toc", ContentsViewSet.as_view({
            "get": "list",
            "post": "create",
            "delete": "destroy",
        })),
    ])),
]
