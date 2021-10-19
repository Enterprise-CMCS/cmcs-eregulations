from django.urls import path

from .views import SupplementalContentView, AbstractLocationView, CategoryView, SupplementalContentTestView

urlpatterns = [
    path("title/<title>/part/<part>/supplemental_content", SupplementalContentView.as_view()),
    path("abstractlocationtest", AbstractLocationView.as_view()),
    path("categorytest", CategoryView.as_view()),
    path("supplementaltest", SupplementalContentTestView.as_view()),
]
