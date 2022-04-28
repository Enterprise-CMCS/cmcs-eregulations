from django.urls import path

from .v3views import (
        SupplementalContentViewSet,
        FRDocListViewSet
)

supplemental_content_view_set = SupplementalContentViewSet.as_view({'put': 'update'})
frdoc_list_view_set = FRDocListViewSet.as_view({'get': 'list'})

urlpatterns = [
        path("supplemental_content", supplemental_content_view_set),
        path("frdoc_list", frdoc_list_view_set),

]
