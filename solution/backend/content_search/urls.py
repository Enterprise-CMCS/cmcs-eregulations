from django.urls import path

from .views import ContentCountViewSet, ContentSearchViewSet, PgVectorSearchViewSet

urlpatterns = [
    path("", ContentSearchViewSet.as_view({
        "get": "list",
    })),
    path("pgvector", PgVectorSearchViewSet.as_view({
        "get": "list",
    }), name="pgvector_search"),
    path("counts", ContentCountViewSet.as_view({
        "get": "list",
    }), name="content_count"),
]
