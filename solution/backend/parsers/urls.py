from django.urls import path

from . import views


urlpatterns = [
    path("config", views.ParserConfigurationViewSet.as_view({
        "get": "retrieve",
    })),
    path("ecfr/results", views.EcfrParserResultViewSet.as_view({
        "get": "list",
        "post": "create",
    })),
    path("ecfr/results/title/<int:title>", views.EcfrParserResultViewSet.as_view({
        "get": "by_title",
    })),
    path("ecfr/results/title/<int:title>/part/<int:part>", views.EcfrParserResultViewSet.as_view({
        "get": "by_title_part",
    })),
    path("ecfr/parts", views.EcfrPartUploadViewSet.as_view({
        "put": "update",
    })),
    path("fr/results", views.FrParserResultViewSet.as_view({
        "get": "list",
        "post": "create",
    })),
]
