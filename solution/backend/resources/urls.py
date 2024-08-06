from django.urls import path

from resources.views import (
    CitationViewSet,
    ContentTextViewSet,
    FederalRegisterLinksNumberViewSet,
    FederalRegisterLinkViewSet,
    InternalCategoryViewSet,
    InternalFileDownloadViewSet,
    InternalFileViewSet,
    InternalLinkViewSet,
    InternalResourceViewSet,
    PublicCategoryViewSet,
    PublicLinkViewSet,
    PublicResourceViewSet,
    ResourceEditViewSet,
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
    path("<int:id>/edit", ResourceEditViewSet.as_view(), name="edit"),
    path("<int:id>/content", ContentTextViewSet.as_view(), name="content"),
    path("public", PublicResourceViewSet.as_view({
        "get": "list",
    })),
    path("public/links", PublicLinkViewSet.as_view({
        "get": "list",
    })),
    path("public/federal_register_links", FederalRegisterLinkViewSet.as_view({
        "get": "list",
        "put": "update",
    })),
    path("public/federal_register_links/document_numbers", FederalRegisterLinksNumberViewSet.as_view({
        "get": "list",
    })),
    path("internal", InternalResourceViewSet.as_view({
        "get": "list",
    })),
    path("internal/files", InternalFileViewSet.as_view({
        "get": "list",
    })),
    path("internal/files/<uid>", InternalFileDownloadViewSet.as_view()),
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
