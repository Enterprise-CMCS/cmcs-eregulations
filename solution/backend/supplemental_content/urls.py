from django.urls import path

from .views import (
        SupplementalContentView,
        SupplementalContentSectionsView,
        SupplementalContentByPartView,
        CategoriesViewSet,
        AllSupplementalContentView,
        SupByLocationViewSet,
        SupByIdViewSet
)
sup_list = SupByIdViewSet.as_view({'get': 'list'})
location_sup_list = SupByLocationViewSet.as_view({'get': 'list'})

category_list = CategoriesViewSet.as_view({'get': 'list'})
urlpatterns = [
        path("title/<title>/part/<part>/supplemental_content", SupplementalContentView.as_view()),
        path("supplemental_content", SupplementalContentSectionsView.as_view()),
        path("supplemental_content_count_by_part", SupplementalContentByPartView.as_view()),
        path("categories", category_list),
        path("locations", location_sup_list, name='location_sup_list'),
        path("sup_by_id/title/<title>/part/<part>", sup_list, name="sup-by-id-list"),
        path("all_sup", AllSupplementalContentView.as_view()),
]
