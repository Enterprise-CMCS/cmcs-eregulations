from django.urls import path

from . import views


urlpatterns = [
    path("ecfr_parser_result/<title>", views.ParserResultViewSet.as_view({
        "get": "retrieve",
        "post": "create",
    })),
    path("part", views.PartUploadViewSet.as_view({
        "put": "update",
    })),
    path("parser_config", views.ParserConfigurationViewSet.as_view({
        "get": "retrieve",
    })),
]
