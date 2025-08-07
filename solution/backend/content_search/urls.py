from django.urls import path

from .views import ContentCountViewSet, ContentSearchViewSet, EmbeddingViewSet, PgVectorSearchView

urlpatterns = [
    path("", ContentSearchViewSet.as_view({
        "get": "list",
    })),
    path("counts", ContentCountViewSet.as_view({
        "get": "list",
    }), name="content_count"),
    path("embeddings/<int:id>", EmbeddingViewSet.as_view(), name="embeddings"),
    path("pgvector", PgVectorSearchView.as_view(), name="pgvector_search_template"),
]
