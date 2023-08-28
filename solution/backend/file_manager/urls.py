from django.urls import path

from .views import UploadedFileViewset

urlpatterns = [
    path("get_file_list", UploadedFileViewset.as_view({
        "get": "list",
    })),
]
