from django.urls import path

from .views import (
    ContentCountViewSet,
    ContentSearchViewSet,
    ResourceChunkUpdateViewSet,
)

urlpatterns = [
    path("", ContentSearchViewSet.as_view({
        "get": "list",
    })),
    path("counts", ContentCountViewSet.as_view({
        "get": "list",
    }), name="content_count"),
    path("resource/<int:pk>/chunk", ResourceChunkUpdateViewSet.as_view({
        "put": "update",
    }), name="resource_chunk_update"),
]
