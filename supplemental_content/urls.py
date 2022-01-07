from django.urls import path

from .views import (
        SupplementalContentView,
        SupplementalContentSectionsView,
        PartsListView,
        CategoryListView,
        SubPartsListView,
        SectionsListView,
        SupplementalContentListView,
)
urlpatterns = [
        path("title/<title>/part/<part>/supplemental_content", SupplementalContentView.as_view()),
        path("api/title/<title>/parts/", PartsListView.as_view()),
        path("api/title/<title>/part/<part>/subParts", SubPartsListView.as_view()),
        path("api/title/<title>/part/<part>/sections", SectionsListView.as_view()),
        path("api/title/<title>/part/<part>/subPart/<subPart>/sections", SectionsListView.as_view()),
        path("api/supplementalContent", SupplementalContentListView.as_view()),
        path("api/categories/", CategoryListView.as_view()),
        path("supplemental_content", SupplementalContentSectionsView.as_view()),
]
