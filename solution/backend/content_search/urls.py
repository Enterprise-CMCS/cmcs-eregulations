from django.urls import path

from .views import (
    ContentCountViewSet,
    ContentSearchViewSet,
    RegTextChunkUpdateViewSet,
    ResourceChunkUpdateViewSet,
)

urlpatterns = [
    path("", ContentSearchViewSet.as_view({
        "get": "list",
        "post": "list",
    })),
    path("counts", ContentCountViewSet.as_view({
        "get": "list",
        "post": "list",
    }), name="content_count"),
    path("resource/<int:pk>/chunk", ResourceChunkUpdateViewSet.as_view({
        "patch": "patch",
    }), name="resource_chunk_update"),
    path("reg_text/<int:pk>/chunk", RegTextChunkUpdateViewSet.as_view({
        "patch": "patch",
    }), name="reg_text_chunk_update"),
]
