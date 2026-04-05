from django.apps import AppConfig


class GrsystemConfig(AppConfig):
    name = 'GRsystem'

    def ready(self):
        import GRsystem.signals  # noqa: F401

