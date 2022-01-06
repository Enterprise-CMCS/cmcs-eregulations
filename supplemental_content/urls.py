from django.urls import path

from .views import SupplementalContentView, SupplementalContentSectionsView, PartsListView

urlpatterns = [
        path("title/<title>/part/<part>/supplemental_content", SupplementalContentView.as_view()),
        path("title/<title>/parts/", PartsListView.as_view() ),
        path("supplemental_content", SupplementalContentSectionsView.as_view()),
]
