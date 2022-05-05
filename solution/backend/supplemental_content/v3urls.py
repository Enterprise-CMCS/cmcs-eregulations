from django.urls import path, include

from .v3views import (
    SupplementalContentViewSet,
    FederalRegisterDocumentViewSet,
    CategoryViewSet,
)


urlpatterns = [
    path("supplemental_content/", include([
        path("", SupplementalContentViewSet.as_view({
            "get": "list",
        })),
        path("frdoc", FederalRegisterDocumentViewSet.as_view({
            "get": "list",
            "put": "update",
        })),
        path("categories", CategoryViewSet.as_view({
            "get": "list",
        })),
        # path("category_tree", CategoryTreeViewSet.as_view({
        #     "get": "list",
        # })),
        # path("location", LocationViewSet.as_view({
        #     "get": "list",
        #     "post": "create",
        # })),
    ])),
]
