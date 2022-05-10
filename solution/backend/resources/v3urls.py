from django.urls import path, include

from .v3views import (
    AbstractResourceViewSet,
    SupplementalContentViewSet,
    FederalRegisterDocsViewSet,
    FederalRegisterDocsNumberViewSet,
    CategoryViewSet,
    CategoryTreeViewSet,
    LocationViewSet,
)


urlpatterns = [
    path("", AbstractResourceViewSet.as_view({
        "get": "list",
    })),
    path("supplemental_content", SupplementalContentViewSet.as_view({
        "get": "list",
    })),
    path("federal_register_docs", FederalRegisterDocsViewSet.as_view({
        "get": "list",
        "put": "update",
    })),
    path("federal_register_docs/doc_numbers", FederalRegisterDocsNumberViewSet.as_view({
        "get": "list",
    })),
    path("categories", CategoryViewSet.as_view({
        "get": "list",
    })),
    path("category_tree", CategoryTreeViewSet.as_view({
        "get": "list",
    })),
    path("locations", LocationViewSet.as_view({
        "get": "list",
        "post": "create",
    })),
]
