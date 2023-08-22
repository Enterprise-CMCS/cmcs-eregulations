from django.urls import path

from .views import file_manager

urlpatterns = [
    path('file_manager/', file_manager, name='file_manager'),
]
