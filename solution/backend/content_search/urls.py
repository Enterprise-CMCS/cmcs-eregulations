from django.urls import path

from .views import ContentSearchViewset, EditContentView, InvokeTextExtractorViewset, PostContentTextViewset

urlpatterns = [
    path("", ContentSearchViewset.as_view({
        "get": "list",
    })),
    path("id/", PostContentTextViewset.as_view(), name='post-content'),
    path('content/<content_id>', InvokeTextExtractorViewset.as_view(), name="call-extractor"),
    path('content/<content_id>/<fr_doc_id>', InvokeTextExtractorViewset.as_view(), name="call-extractor"),
    path('resource/<resource_id>', EditContentView.as_view(), name="edit-content"),
]
