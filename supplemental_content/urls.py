from django.urls import path

from .views import AbstractLocationView

#urlpatterns = [path("title/<title>/part/<part>/supplemental_content", SupplementalContentView.as_view())]
urlpatterns = [path("abstractlocationtest", AbstractLocationView.as_view())]
