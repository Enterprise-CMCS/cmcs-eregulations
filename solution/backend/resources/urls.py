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

# TODO: remove these endpoints after v3 move is complete

category_list = CategoriesViewSet.as_view({'get': 'list'})
urlpatterns = [
    path("title/<int:title>/part/<int:part>/supplemental_content", SupplementalContentView.as_view()),
    path("supplemental_content", SupplementalContentSectionsView.as_view()),
    path("supplemental_content_count_by_part", SupplementalContentByPartView.as_view()),
    path("categories", category_list),
    path("locations", location_sup_list, name='location_sup_list'),
    path("sup_by_id/title/<int:title>/part/<int:part>", sup_list, name="sup-by-id-list"),
    path("all_sup", AllSupplementalContentView.as_view()),
]
