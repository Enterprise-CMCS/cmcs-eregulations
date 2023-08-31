from django.urls import path

from .views import SubjectViewset, UploadCategoryViewset, UploadedFileViewset

urlpatterns = [
    path("upload_categories", UploadCategoryViewset.as_view({
        "get": "list",
    })),
    path("subjects", SubjectViewset.as_view({
        "get": "list",
    })),
    path("file_list", UploadedFileViewset.as_view({
        "get": "list",
    })),
    path("id/<id>", UploadedFileViewset.as_view({
        "get": "retrieve",
    })),
    path("file/<file_id>", UploadedFileViewset.as_view({
        "get": "download",
    }), name="file-download"),
]
