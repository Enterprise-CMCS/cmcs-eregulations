from django.urls import path

from resources.v3views import (
    categories,
    locations,
    resources,
)


urlpatterns = [
    path("search", resources.ResourceSearchViewSet.as_view({
      "get": "list",
    })),
    path("", resources.AbstractResourceViewSet.as_view({
        "get": "list",
    })),
    path("supplemental_content", resources.SupplementalContentViewSet.as_view({
        "get": "list",
    })),
    path("federal_register_docs", resources.FederalRegisterDocsViewSet.as_view({
        "get": "list",
        "put": "update",
    })),
    path("federal_register_docs/doc_numbers", resources.FederalRegisterDocsNumberViewSet.as_view({
        "get": "list",
    })),
    path("categories", categories.CategoryViewSet.as_view({
        "get": "list",
    })),
    path("categories/tree", categories.CategoryTreeViewSet.as_view({
        "get": "list",
    })),
    path("locations", locations.LocationViewSet.as_view({
        "get": "list",
    })),
    path("locations/sections", locations.SectionViewSet.as_view({
        "get": "list",
    })),
    path("locations/subparts", locations.SubpartViewSet.as_view({
        "get": "list",
    })),
]
