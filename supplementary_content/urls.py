from django.urls import path

from .views import (
    SupplementaryContentView,
)

urlpatterns = [path("title/<title>/part/<part>/supplementary_content", SupplementaryContentView.as_view()),]
