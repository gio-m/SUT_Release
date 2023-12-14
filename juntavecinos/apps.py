from django.apps import AppConfig


class JuntavecinosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'juntavecinos'

    def ready(self):
        import juntavecinos.signals