from django.apps import AppConfig
from django.db.models.signals import post_save 


class RegSearchConfig(AppConfig):
    name = "regcore.search"
    verbose_name = "postgres based search for regulations"

    def ready(self):
        from .models import update_search

        post_save.connect(update_search, sender="regcore.Part")
