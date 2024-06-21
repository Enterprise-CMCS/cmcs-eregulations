from django.urls import path

from .views import ContentSearchViewSet, EditContentView, InvokeTextExtractorViewset, PostContentTextViewset

urlpatterns = [
    path("", ContentSearchViewSet.as_view({
        "get": "list",
        "post": "post",
    })),
]
