from django.urls import path

from .views import ContentSearchViewset, InvokeTextExtractorViewset, PostContentTextViewset

urlpatterns = [
    path("", ContentSearchViewset.as_view({
        "get": "list",
    })),
    path("id/", PostContentTextViewset.as_view({
        "post": 'update',
    })),
    path('content/', InvokeTextExtractorViewset.as_view({
        "post": 'extract'
    }))
]
