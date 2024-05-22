from django.apps import AppConfig

class UserConfig(AppConfig):
    name = 'user'

    def ready(self):
        import user.models  # noqa: F401 (imported but unused)
