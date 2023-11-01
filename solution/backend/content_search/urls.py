from django.urls import path

from .views import ContentSearchViewset, PostContentTextViewset

urlpatterns = [
    path("", ContentSearchViewset.as_view({
        "get": "list",
    })),
    path("id/", PostContentTextViewset.as_view()),
]
