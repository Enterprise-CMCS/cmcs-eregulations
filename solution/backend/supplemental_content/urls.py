from django.urls import path

from .views import SupplementalContentView, SupplementalContentSectionsView, SupplementalContentByPartView

urlpatterns = [
        path("title/<title>/part/<part>/supplemental_content", SupplementalContentView.as_view()),
        path("supplemental_content", SupplementalContentSectionsView.as_view()),
        path("supplemental_content_count_by_part", SupplementalContentByPartView.as_view())
]
