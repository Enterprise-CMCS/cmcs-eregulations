from django.urls import path, include
from regcore.views import (
    EffectivePartView,
    EffectiveTitlesView,
    EffectivePartsView,
    EffectivePartTocView,
    PartsView,
)


urlpatterns = [
    path("v2/", include([
        path("", include('regcore.search.urls')),
        path("", include('supplementary_content.urls')),
        path("", PartsView.as_view(), name="regcore"),
        path("title/<title>/part/<name>", PartsView.as_view()),
        path("<date>", EffectiveTitlesView.as_view()),
        path("<date>/title/<title>", EffectivePartsView.as_view()),
        path("<date>/title/<title>/part/<name>", EffectivePartView.as_view()),
        path("<date>/title/<title>/part/<name>/toc", EffectivePartTocView.as_view()),
    ]))
]
