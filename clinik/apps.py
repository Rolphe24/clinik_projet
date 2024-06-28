from django.apps import AppConfig
from django.apps import AppConfig

class ClinikConfig(AppConfig):
    name = 'clinik'

    def ready(self):
        import clinik.signals


class ClinikConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clinik'
