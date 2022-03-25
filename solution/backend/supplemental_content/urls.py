from django.urls import path

from .views import (
        SupplementalContentView,
        SupplementalContentSectionsView,
        SupplementalContentByPartView,
        CategoriesViewSet,
        AllSupplementalContentView
)
category_list = CategoriesViewSet.as_view({'get': 'list'})
urlpatterns = [
        path("title/<title>/part/<part>/supplemental_content", SupplementalContentView.as_view()),
        path("supplemental_content", SupplementalContentSectionsView.as_view()),
        path("supplemental_content_count_by_part", SupplementalContentByPartView.as_view()),
        path("categories", category_list),
        path("all_sup", AllSupplementalContentView.as_view()),
]
