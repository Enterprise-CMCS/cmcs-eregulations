from django.urls import path

from .views import ContentSearchViewSet, PostContentTextViewset

urlpatterns = [
    path("", ContentSearchViewSet.as_view({
        "get": "list",
    })),
    path("upload", PostContentTextViewset.as_view(), name='post-content'),
]
