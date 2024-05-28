from django.urls import path

from resources.views import (
    CitationViewSet,
    InternalCategoryViewSet,
    PublicCategoryViewSet,
    ResourceGroupViewSet,
    SectionViewSet,
    SubjectViewSet,
    SubpartViewSet,
)

urlpatterns = [
    # path("", ResourceViewSet.as_view({
    #     "get": "list",
    # })),
    # path("federal_register_links", FederalRegisterLinkViewSet.as_view({
    #     "get": "list",
    #     "put": "update",
    # })),
    # path("federal_register_links/document_numbers", FederalRegisterLinkDocNumViewSet.as_view({
    #     "get": "list",
    # })),
    # path("public_links", PublicLinkViewSet.as_view({
    #     "get": "list",
    # })),
    # path("internal_files", InternalFileViewSet.as_view({
    #     "get": "list",
    # })),
    # path("internal_links", InternalLinkViewSet.as_view({
    #     "get": "list",
    # })),
    path("resource_groups", ResourceGroupViewSet.as_view({
        "get": "list",
    })),
    path("public_categories", PublicCategoryViewSet.as_view({
        "get": "list",
    })),
    path("internal_categories", InternalCategoryViewSet.as_view({
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
