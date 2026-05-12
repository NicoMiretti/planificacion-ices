from django.apps import AppConfig


class InstanciasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.instancias'
    verbose_name = 'Instancias de Presentación'

    def ready(self):
        import apps.instancias.signals  # noqa: F401
