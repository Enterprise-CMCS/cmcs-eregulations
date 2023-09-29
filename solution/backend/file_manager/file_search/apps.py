from django.apps import AppConfig
from django.db.models.signals import post_save


class FileSearchConfig(AppConfig):
    name = "file_manager.file_search"
    verbose_name = "postgres based search for uploaded files"

    def ready(self):
        from .models import update_search

        post_save.connect(update_search, sender="file_manager.UploadedFile")
