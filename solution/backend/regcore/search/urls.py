from django.urls import path

from .views import (
    SearchView,
    SupplementalContentSearchViewSet,
)

urlpatterns = [
    path("search", SearchView.as_view()),
    path("supplemental_content/search", SupplementalContentSearchViewSet.as_view({
        "get": "list",
    })),
]
