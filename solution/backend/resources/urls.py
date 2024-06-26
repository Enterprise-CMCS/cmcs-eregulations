from django.urls import path

from resources.views import (
    CitationViewSet,
    FederalRegisterLinkViewSet,
    InternalCategoryViewSet,
    InternalFileViewSet,
    InternalLinkViewSet,
    InternalResourceViewSet,
    PublicCategoryViewSet,
    PublicLinkViewSet,
    PublicResourceViewSet,
    ResourceGroupViewSet,
    ResourceViewSet,
    SectionViewSet,
    SubjectViewSet,
    SubpartViewSet,
)

urlpatterns = [
    path("", ResourceViewSet.as_view({
        "get": "list",
    })),
    path("public", PublicResourceViewSet.as_view({
        "get": "list",
    })),
    path("public/links", PublicLinkViewSet.as_view({
        "get": "list",
    })),
    path("public/federal_register_links", FederalRegisterLinkViewSet.as_view({
        "get": "list",
    })),
    # path("public/federal_register_links/document_numbers", FederalRegisterLinkDocumentNumberViewSet.as_view({
    #     "get": "list",
    # })),
    path("internal", InternalResourceViewSet.as_view({
        "get": "list",
    })),
    path("internal/files", InternalFileViewSet.as_view({
        "get": "list",
    })),
    path("internal/links", InternalLinkViewSet.as_view({
        "get": "list",
    })),
    path("resource_groups", ResourceGroupViewSet.as_view({
        "get": "list",
    })),
    path("public/categories", PublicCategoryViewSet.as_view({
        "get": "list",
    })),
    path("internal/categories", InternalCategoryViewSet.as_view({
        "get": "list",
    })),
    path("subjects", SubjectViewSet.as_view({
        "get": "list",
    })),
    path("citations", CitationViewSet.as_view({
        "get": "list",
    })),
    path("citations/sections", SectionViewSet.as_view({
        "get": "list",
    })),
    path("citations/subparts", SubpartViewSet.as_view({
        "get": "list",
    })),
]
