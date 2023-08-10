from .views import file_manager

from django.urls import path

urlpatterns = [
    path('file_manager/', file_manager, name='file_manager'),
]
