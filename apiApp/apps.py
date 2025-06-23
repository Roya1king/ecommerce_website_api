from django.apps import AppConfig


class ApiappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apiApp"

    def ready(self):
        # Import signals to ensure they are registered
        import apiApp.signals  # noqa: F401