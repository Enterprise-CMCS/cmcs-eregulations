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
)


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
    ]))
]
