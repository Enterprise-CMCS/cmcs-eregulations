from django.apps import AppConfig


class FileSearchConfig(AppConfig):
    name = "content_search"
    verbose_name = "postgres based search for uploaded files and abstract resources"

    def ready(self):
        import content_search.signals # noqa
