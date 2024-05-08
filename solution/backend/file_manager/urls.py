from django.urls import path

from .views import (
    DivisionViewset,
    GroupViewset,
    RepoCategoryViewSet,
    RepositoryCategoryTreeViewSet,
    SubjectViewset,
    TopSubjectsByLocationViewSet,
    UploadedFileViewset,
)

urlpatterns = [
    path("categories", RepoCategoryViewSet.as_view({
        "get": "list",
    })),
    path("categories/tree", RepositoryCategoryTreeViewSet.as_view({
        "get": "list",
    })),
    path("subjects", SubjectViewset.as_view({
        "get": "list",
    })),
    path("subjects/top_by_location", TopSubjectsByLocationViewSet.as_view({
        "get": "list",
    }), name='top-subjects-by-location'),
    path("groups", GroupViewset.as_view({
        "get": "list",
    })),
    path("divisions", DivisionViewset.as_view({
        "get": "list",
    })),
    path("files", UploadedFileViewset.as_view({
        "get": "list",
    })),
    path("files/<id>/info", UploadedFileViewset.as_view({
        "get": "retrieve",
    })),
    path("files/<file_id>", UploadedFileViewset.as_view({
        "get": "download",
    }), name="file-download"),
    path("files/<file_id>/file-name/<file_name>", UploadedFileViewset.as_view({
        "put": "upload",
    }), name="file-upload"),
    path("file-name/<file_name>", UploadedFileViewset.as_view({
        "post": "upload",
    }), name="file-upload-new"),
]
