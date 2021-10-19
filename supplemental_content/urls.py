from django.urls import path

from .views import SupplementalContentView

urlpatterns = [path("title/<title>/part/<part>/supplemental_content", SupplementalContentView.as_view())]
