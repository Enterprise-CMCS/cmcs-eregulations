from django.urls import path

from .v3views import (
        SupplementalContentViewSet
)

supplemental_content_view_set = SupplementalContentViewSet.as_view({'put': 'update'})

urlpatterns = [
        path("supplemental_content", supplemental_content_view_set),
]