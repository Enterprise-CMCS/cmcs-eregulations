from django.urls import path, include

from .v3views import (
    SupplementalContentViewSet,
    FederalRegisterDocumentViewSet,
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
    ])),
]
