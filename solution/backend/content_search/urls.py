from django.urls import path

from .views import ContentSearchViewset

urlpatterns = [
    path("", ContentSearchViewset.as_view({
        "get": "list",
    })),
]
