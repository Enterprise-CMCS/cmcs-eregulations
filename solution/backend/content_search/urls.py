from django.urls import path

from .views import ContentCountViewSet, ContentSearchViewSet, PgVectorSearchView

urlpatterns = [
    path("", ContentSearchViewSet.as_view({
        "get": "list",
    })),
    path("counts", ContentCountViewSet.as_view({
        "get": "list",
    }), name="content_count"),
    path("pgvector", PgVectorSearchView.as_view(), name="pgvector_search_template"),
]
