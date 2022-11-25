from django.urls import path

from .v3views import V3SearchView

urlpatterns = [
    path("search", V3SearchView.as_view({
        "get": "list",
    })),
]
