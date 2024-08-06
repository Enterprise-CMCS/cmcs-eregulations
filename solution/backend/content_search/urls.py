from django.urls import path

from .views import ContentSearchViewSet

urlpatterns = [
    path("", ContentSearchViewSet.as_view({
        "get": "list",
    })),
]
