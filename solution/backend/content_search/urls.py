from django.urls import path

from .views import ContentCountViewSet, ContentSearchViewSet

urlpatterns = [
    path("", ContentSearchViewSet.as_view({
        "get": "list",
    })),
    path("counts", ContentCountViewSet.as_view({
        "get": "list",
    }), name="content_count"),
]
